from typing import List, Tuple, Any, Optional
from src.models import UserProfileInput
from pydantic import ValidationError

def clean_string_list(items: Optional[str]) -> List[str]:
    """
    Parses a comma-separated string into a list of cleaned, non-empty strings.
    """
    if not items:
        return []
    # Split by comma, strip whitespace, and ignore empty values
    return [x.strip() for x in items.split(",") if x.strip()]

def validate_profile_input(
    habit_type: str,
    declared_triggers: str,
    reduction_goal: str
) -> Tuple[bool, str, Optional[UserProfileInput]]:
    """
    Validates onboarding details before creating the plan and storing in the DB.
    """
    try:
        cleaned_habit = habit_type.strip()
        if not cleaned_habit:
            return False, "Please select or type a harmful digital habit to track.", None
            
        triggers_list = clean_string_list(declared_triggers)
        if not triggers_list:
            return False, "Please specify at least one trigger (e.g. boredom, morning waking, stress).", None
            
        cleaned_goal = reduction_goal.strip()
        if not cleaned_goal:
            return False, "Please specify a clear reduction goal (e.g. '8hrs to 3hrs daily').", None
            
        # Pydantic validation
        profile_input = UserProfileInput(
            habit_type=cleaned_habit,
            declared_triggers=triggers_list,
            reduction_goal=cleaned_goal
        )
        return True, "", profile_input
        
    except ValidationError as e:
        error_msgs = []
        for error in e.errors():
            loc = error.get("loc", ["input"])[0]
            msg = error.get("msg", "Invalid value")
            error_msgs.append(f"'{loc}': {msg}")
        return False, "Validation Error: " + ", ".join(error_msgs), None

def validate_screen_time(screen_time_str: Any) -> Tuple[bool, str, Optional[int]]:
    """
    Validates logged screen time.
    """
    try:
        val = int(screen_time_str)
        if val < 0:
            return False, "Screen time cannot be a negative value.", None
        if val > 24 * 60:
            return False, "Screen time cannot exceed 24 hours (1440 minutes).", None
        return True, "", val
    except (ValueError, TypeError):
        return False, "Screen time must be a valid integer representing minutes or hours.", None
