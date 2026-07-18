from src.validators import clean_string_list, validate_profile_input, validate_screen_time

def test_clean_string_list():
    assert clean_string_list("boredom, stress, mornings") == ["boredom", "stress", "mornings"]
    assert clean_string_list("  boredom ,  stress  ") == ["boredom", "stress"]
    assert clean_string_list("") == []
    assert clean_string_list(None) == []

def test_validate_profile_input_valid():
    is_valid, err, val = validate_profile_input(
        habit_type="Doom-scrolling (TikTok/Instagram Reels)",
        declared_triggers="stress, boredom",
        reduction_goal="Reduce from 6hrs to 2hrs daily"
    )
    assert is_valid is True
    assert err == ""
    assert val is not None
    assert val.habit_type == "Doom-scrolling (TikTok/Instagram Reels)"
    assert val.declared_triggers == ["stress", "boredom"]
    assert val.reduction_goal == "Reduce from 6hrs to 2hrs daily"

def test_validate_profile_input_invalid():
    is_valid, err, val = validate_profile_input(
        habit_type="",
        declared_triggers="stress",
        reduction_goal="Reduce from 6hrs to 2hrs daily"
    )
    assert is_valid is False
    assert "Please select or type a harmful digital habit" in err
    assert val is None

def test_validate_screen_time_valid():
    is_valid, err, val = validate_screen_time("120")
    assert is_valid is True
    assert err == ""
    assert val == 120

def test_validate_screen_time_invalid():
    is_valid, err, val = validate_screen_time("-10")
    assert is_valid is False
    assert "Screen time cannot be a negative value" in err
    assert val is None
