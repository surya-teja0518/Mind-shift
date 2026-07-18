import os
from src.database import init_db, save_profile, get_profile, log_session, get_recent_logs, get_streak, update_streak, clear_db

def test_database_and_streaks():
    # Start with a clean database for testing
    clear_db()
    
    # 1. Initialize DB
    init_db()
    assert os.path.exists("mindshift.db") is True
    
    # 2. Test saving and fetching user profile
    save_profile(
        habit_type="Doom-scrolling",
        declared_triggers=["stress", "boredom"],
        reduction_goal="Reduce from 6h to 2h",
        thirty_day_plan="Step 1: Test"
    )
    
    profile = get_profile()
    assert profile is not None
    assert profile["habit_type"] == "Doom-scrolling"
    assert profile["declared_triggers"] == ["stress", "boredom"]
    assert profile["reduction_goal"] == "Reduce from 6h to 2h"
    assert profile["thirty_day_plan"] == "Step 1: Test"
    
    # 3. Test default streaks
    streak = get_streak()
    assert streak["count"] == 0
    assert streak["type"] == "habit"
    
    # 4. Test updating streak
    update_streak(5, "recovery")
    streak = get_streak()
    assert streak["count"] == 5
    assert streak["type"] == "recovery"
    
    # 5. Test logging sessions
    log_session(
        session_type="checkin",
        user_input_text="I feel calm today",
        emotional_state_detected="calm",
        coaching_persona_used="supportive",
        micro_goal_delivered="Do 10 pushups",
        flags_raised=["milestone_reached"],
        actual_screen_time=120
    )
    
    recent_logs = get_recent_logs(limit=1)
    assert len(recent_logs) == 1
    log = recent_logs[0]
    assert log["session_type"] == "checkin"
    assert log["user_input_text"] == "I feel calm today"
    assert log["emotional_state_detected"] == "calm"
    assert log["coaching_persona_used"] == "supportive"
    assert log["micro_goal_delivered"] == "Do 10 pushups"
    assert log["flags_raised"] == ["milestone_reached"]
    assert log["actual_screen_time"] == 120
    
    # Clean up database after testing
    clear_db()
