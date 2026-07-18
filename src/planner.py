from datetime import datetime
from typing import Any, List
from src.models import MindShiftResponse, UserProfileInput
from src.prompts import ONBOARDING_PLAN_PROMPT, CHECKIN_PROMPT, RELAPSE_PROMPT, INSIGHT_PROMPT
from src.gemini import generate_coaching_response, generate_onboarding_plan
from src.database import save_profile, get_profile, log_session, get_recent_logs, get_streak, update_streak
from src.utils import get_logger

logger = get_logger()

def onboard_user(input_data: UserProfileInput) -> str:
    """
    Orchestrates onboarding:
    1. Triggers Gemini to generate a personalized 30-day plan.
    2. Stores the profile and plan in the SQLite database.
    3. Returns the plan string.
    """
    logger.info(f"Onboarding user. Habit: {input_data.habit_type}, Goal: {input_data.reduction_goal}")
    
    triggers_str = ", ".join(input_data.declared_triggers)
    prompt = ONBOARDING_PLAN_PROMPT.format(
        habit_type=input_data.habit_type,
        triggers_str=triggers_str,
        reduction_goal=input_data.reduction_goal
    )
    
    # Generate 30-day plan
    plan_text = generate_onboarding_plan(prompt)
    
    # Save to SQLite
    save_profile(
        habit_type=input_data.habit_type,
        declared_triggers=input_data.declared_triggers,
        reduction_goal=input_data.reduction_goal,
        thirty_day_plan=plan_text
    )
    
    return plan_text

def process_checkin(user_input: str, actual_screen_time: Any = None) -> MindShiftResponse:
    """
    Handles user check-ins:
    1. Fetches profile and log history for context.
    2. Requests Gemini coaching response.
    3. Manages streaks (increments by 1 if successfully checked in).
    4. Records logs.
    """
    logger.info("Processing daily check-in...")
    
    profile = get_profile()
    if not profile:
        raise ValueError("No user profile found. Please complete onboarding first.")
        
    triggers_str = ", ".join(profile["declared_triggers"])
    
    # Calculate days in program
    start_date = datetime.fromisoformat(profile["program_start_date"])
    days_in_program = (datetime.now() - start_date).days + 1
    
    # Retrieve streak & recent history
    streak = get_streak()
    recent_logs = get_recent_logs(limit=3)
    
    # Format history string
    history_lines = []
    for log in reversed(recent_logs):
        history_lines.append(
            f"- User said: '{log['user_input_text']}' | State: {log['emotional_state_detected']} | "
            f"Persona: {log['coaching_persona_used']} | Goal set: '{log['micro_goal_delivered']}'"
        )
    history_str = "\n".join(history_lines) if history_lines else "No previous sessions logged yet."
    
    last_emotional_state = recent_logs[0]["emotional_state_detected"] if recent_logs else "calm"
    last_micro_goal = recent_logs[0]["micro_goal_delivered"] if recent_logs else "None"
    
    # Build prompt
    prompt = CHECKIN_PROMPT.format(
        habit_type=profile["habit_type"],
        triggers_str=triggers_str,
        reduction_goal=profile["reduction_goal"],
        days_in_program=days_in_program,
        streak_count=streak["count"],
        streak_type=streak["type"],
        last_emotional_state=last_emotional_state,
        last_micro_goal=last_micro_goal,
        relapse_status="Inactive" if streak["type"] == "habit" else "Active Recovery Mode",
        history_str=history_str,
        user_input=user_input
    )
    
    # Call Gemini
    response = generate_coaching_response(prompt)
    
    # Get last updated date and today's date to check if it is the same day
    last_updated_date = streak.get("last_updated", "")[:10]
    today_date = datetime.now().strftime("%Y-%m-%d")
    is_same_day = (last_updated_date == today_date)

    # Update Streak:
    # If the detected state is "relapsing", it will go to the relapse handler.
    # Otherwise, check-ins increment the streak.
    if response.emotional_state == "relapsing" or "relapse_risk" in response.flags:
        # Shift to recovery mode but keep count
        update_streak(streak["count"], "recovery")
    else:
        # Increment streak
        # If it was a recovery streak, we can transition back to habit streak after a good check-in
        new_type = "habit" if streak["type"] == "recovery" else streak["type"]
        if is_same_day:
            update_streak(streak["count"], new_type)
        else:
            update_streak(streak["count"] + 1, new_type)
        
    # Log session
    log_session(
        session_type="checkin",
        user_input_text=user_input,
        emotional_state_detected=response.emotional_state,
        coaching_persona_used=response.coaching_persona,
        micro_goal_delivered=response.micro_goal,
        flags_raised=response.flags,
        actual_screen_time=actual_screen_time
    )
    
    return response

def process_relapse(user_input: str) -> MindShiftResponse:
    """
    Handles a self-reported relapse:
    1. Fetches profile and streak details.
    2. Switches streak_type to "recovery" (maintaining the streak count).
    3. Calls relapse prompt.
    4. Logs to SQLite database.
    """
    logger.info("Processing self-reported relapse...")
    
    profile = get_profile()
    if not profile:
        raise ValueError("No user profile found. Please complete onboarding first.")
        
    triggers_str = ", ".join(profile["declared_triggers"])
    streak = get_streak()
    
    # Keep the streak count but set type to recovery
    update_streak(streak["count"], "recovery")
    
    prompt = RELAPSE_PROMPT.format(
        habit_type=profile["habit_type"],
        triggers_str=triggers_str,
        streak_count=streak["count"],
        user_input=user_input
    )
    
    response = generate_coaching_response(prompt)
    
    log_session(
        session_type="relapse",
        user_input_text=user_input,
        emotional_state_detected=response.emotional_state,
        coaching_persona_used=response.coaching_persona,
        micro_goal_delivered=response.micro_goal,
        flags_raised=response.flags
    )
    
    return response

def generate_weekly_insight() -> str:
    """
    Generates a conversational weekly insight narrative from the database logs.
    """
    logger.info("Generating weekly recovery insights...")
    profile = get_profile()
    if not profile:
        return "Complete onboarding to begin generating insights."
        
    recent_logs = get_recent_logs(limit=10)
    if not recent_logs:
        return "No check-ins logged yet. Complete your first daily check-in to unlock insights."
        
    log_summaries = []
    for log in reversed(recent_logs):
        log_summaries.append(
            f"- Date: {log['timestamp'][:10]} | Type: {log['session_type']} | Input: '{log['user_input_text']}' | "
            f"State detected: {log['emotional_state_detected']} | Goal: '{log['micro_goal_delivered']}'"
        )
    logs_summary = "\n".join(log_summaries)
    
    prompt = INSIGHT_PROMPT.format(
        habit_type=profile["habit_type"],
        reduction_goal=profile["reduction_goal"],
        logs_summary=logs_summary
    )
    
    try:
        from src.gemini import generate_insight_response
        return generate_insight_response(prompt)
    except Exception as e:
        logger.error(f"Failed to generate weekly insight: {str(e)}")
        
    return "Your progress is steady. You are logging check-ins and facing your triggers with high awareness. Keep moving one day at a time."
