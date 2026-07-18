import sqlite3
import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.utils import get_logger

logger = get_logger()
DB_PATH = "mindshift.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """
    Initializes the SQLite database and creates tables if they don't exist.
    """
    logger.info("Initializing SQLite database schema...")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # User profile table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                user_id TEXT PRIMARY KEY,
                habit_type TEXT NOT NULL,
                declared_triggers TEXT NOT NULL, -- JSON list of strings
                reduction_goal TEXT NOT NULL,
                program_start_date TEXT NOT NULL,
                thirty_day_plan TEXT NOT NULL -- Long text
            )
        """)
        
        # Session logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_logs (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_type TEXT NOT NULL, -- "checkin" | "nudge" | "relapse" | "sos"
                user_input_text TEXT NOT NULL,
                emotional_state_detected TEXT NOT NULL,
                coaching_persona_used TEXT NOT NULL,
                micro_goal_delivered TEXT NOT NULL,
                flags_raised TEXT NOT NULL, -- JSON list of strings
                actual_screen_time INTEGER -- Nullable
            )
        """)
        
        # Streak records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS streak_records (
                id INTEGER PRIMARY KEY CHECK (id = 1), -- Ensures single row
                streak_count INTEGER NOT NULL DEFAULT 0,
                streak_type TEXT NOT NULL DEFAULT 'habit', -- 'habit' | 'recovery'
                last_updated TEXT NOT NULL
            )
        """)
        
        # Initialize default streak if not present
        cursor.execute("SELECT COUNT(*) FROM streak_records")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO streak_records (id, streak_count, streak_type, last_updated)
                VALUES (1, 0, 'habit', ?)
            """, (datetime.now().isoformat(),))
            
        conn.commit()
        logger.info("SQLite database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {str(e)}", exc_info=True)
        raise
    finally:
        conn.close()

def save_profile(habit_type: str, declared_triggers: List[str], reduction_goal: str, thirty_day_plan: str) -> None:
    """
    Saves or overwrites the user profile in the database.
    """
    init_db()  # Ensure tables exist
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        triggers_json = json.dumps(declared_triggers)
        start_date = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO user_profile (user_id, habit_type, declared_triggers, reduction_goal, program_start_date, thirty_day_plan)
            VALUES ('current_user', ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                habit_type = excluded.habit_type,
                declared_triggers = excluded.declared_triggers,
                reduction_goal = excluded.reduction_goal,
                thirty_day_plan = excluded.thirty_day_plan
        """, (habit_type, triggers_json, reduction_goal, start_date, thirty_day_plan))
        
        # Reset streaks for a new profile
        cursor.execute("""
            UPDATE streak_records 
            SET streak_count = 0, streak_type = 'habit', last_updated = ? 
            WHERE id = 1
        """, (start_date,))
        
        # Clear existing logs for fresh start
        cursor.execute("DELETE FROM session_logs")
        
        conn.commit()
        logger.info("User profile saved and session state reset.")
    except Exception as e:
        logger.error(f"Error saving user profile: {str(e)}", exc_info=True)
        raise
    finally:
        conn.close()

def get_profile() -> Optional[Dict[str, Any]]:
    """
    Retrieves the user profile if it exists.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile WHERE user_id = 'current_user'")
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "habit_type": row["habit_type"],
            "declared_triggers": json.loads(row["declared_triggers"]),
            "reduction_goal": row["reduction_goal"],
            "program_start_date": row["program_start_date"],
            "thirty_day_plan": row["thirty_day_plan"]
        }
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}", exc_info=True)
        return None
    finally:
        conn.close()

def log_session(
    session_type: str, 
    user_input_text: str, 
    emotional_state_detected: str, 
    coaching_persona_used: str, 
    micro_goal_delivered: str, 
    flags_raised: List[str], 
    actual_screen_time: Optional[int] = None
) -> None:
    """
    Appends a new interaction log to the database.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        flags_json = json.dumps(flags_raised)
        
        cursor.execute("""
            INSERT INTO session_logs (timestamp, session_type, user_input_text, emotional_state_detected, coaching_persona_used, micro_goal_delivered, flags_raised, actual_screen_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, session_type, user_input_text, emotional_state_detected, coaching_persona_used, micro_goal_delivered, flags_json, actual_screen_time))
        
        conn.commit()
        logger.info(f"Logged {session_type} session to database.")
    except Exception as e:
        logger.error(f"Error logging session: {str(e)}", exc_info=True)
    finally:
        conn.close()

def get_recent_logs(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieves the most recent session logs.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM session_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            logs.append({
                "timestamp": row["timestamp"],
                "session_type": row["session_type"],
                "user_input_text": row["user_input_text"],
                "emotional_state_detected": row["emotional_state_detected"],
                "coaching_persona_used": row["coaching_persona_used"],
                "micro_goal_delivered": row["micro_goal_delivered"],
                "flags_raised": json.loads(row["flags_raised"]),
                "actual_screen_time": row["actual_screen_time"]
            })
        return logs
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}", exc_info=True)
        return []
    finally:
        conn.close()

def get_streak() -> Dict[str, Any]:
    """
    Gets the current streak count, type, and last updated time.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM streak_records WHERE id = 1")
        row = cursor.fetchone()
        if not row:
            return {"count": 0, "type": "habit", "last_updated": ""}
        return {
            "count": row["streak_count"],
            "type": row["streak_type"],
            "last_updated": row["last_updated"]
        }
    except Exception as e:
        logger.error(f"Error fetching streak: {str(e)}", exc_info=True)
        return {"count": 0, "type": "habit", "last_updated": ""}
    finally:
        conn.close()

def update_streak(count: int, streak_type: str) -> None:
    """
    Updates the streak parameters.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute("""
            UPDATE streak_records 
            SET streak_count = ?, streak_type = ?, last_updated = ? 
            WHERE id = 1
        """, (count, streak_type, timestamp))
        conn.commit()
        logger.info(f"Streak updated to: {count} ({streak_type})")
    except Exception as e:
        logger.error(f"Error updating streak: {str(e)}", exc_info=True)
    finally:
        conn.close()

def clear_db() -> None:
    """
    Resets the database completely.
    """
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            logger.info("Cleared local SQLite database file.")
        except Exception as e:
            logger.error(f"Error removing database file: {str(e)}")
