from pydantic import BaseModel, Field
from typing import List, Literal

class MindShiftResponse(BaseModel):
    emotional_state: Literal["stressed", "calm", "anxious", "motivated", "relapsing"] = Field(
        ..., description="Detected emotional state of the user based on check-in text"
    )
    coaching_persona: Literal["supportive", "firm", "celebratory", "crisis"] = Field(
        ..., description="Coaching persona selected to match user's emotional state"
    )
    primary_message: str = Field(
        ..., description="Empathetic, personalized coaching response (never robotic)"
    )
    micro_goal: str = Field(
        ..., description="One small, highly actionable micro-goal for the day"
    )
    nudge_intensity: Literal["low", "medium", "high"] = Field(
        ..., description="Nudge intensity based on user stress/relapse risk"
    )
    follow_up_prompt: str = Field(
        ..., description="Engaging follow-up question to keep the user reflective"
    )
    flags: List[str] = Field(
        default_factory=list,
        description="Flags mapping to UI triggers (e.g., 'relapse_risk', 'milestone_reached', 'pattern_detected')"
    )

class UserProfileInput(BaseModel):
    habit_type: str = Field(..., description="Habit selection (e.g. Doom-scrolling, Social media)")
    declared_triggers: List[str] = Field(..., description="List of triggers identified by the user")
    reduction_goal: str = Field(..., description="Target screen time / limit (e.g. 8hrs to 3hrs daily)")
