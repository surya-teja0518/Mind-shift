import json
import time
import urllib.request
from src.models import MindShiftResponse
from src.prompts import SYSTEM_INSTRUCTIONS
from src.utils import get_gemini_api_key, get_gemini_model, get_logger

logger = get_logger()

def call_gemini_raw_http(prompt_text: str, is_json_response: bool = False) -> str:
    """
    Makes a raw HTTP POST request to the Google Gemini API REST endpoint using python's built-in urllib.
    Requires no external SDK dependencies.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or secrets.")

    model = get_gemini_model()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # Build payload structure matching Google's REST specification
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    if is_json_response:
        payload["systemInstruction"] = {
            "parts": [{"text": SYSTEM_INSTRUCTIONS}]
        }
        payload["generationConfig"] = {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "emotional_state": {
                        "type": "STRING",
                        "enum": ["stressed", "calm", "anxious", "motivated", "relapsing"]
                    },
                    "coaching_persona": {
                        "type": "STRING",
                        "enum": ["supportive", "firm", "celebratory", "crisis"]
                    },
                    "primary_message": {"type": "STRING"},
                    "micro_goal": {"type": "STRING"},
                    "nudge_intensity": {
                        "type": "STRING",
                        "enum": ["low", "medium", "high"]
                    },
                    "follow_up_prompt": {"type": "STRING"},
                    "flags": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                },
                "required": [
                    "emotional_state", 
                    "coaching_persona", 
                    "primary_message", 
                    "micro_goal", 
                    "nudge_intensity", 
                    "follow_up_prompt", 
                    "flags"
                ]
            }
        }
    else:
        payload["generationConfig"] = {
            "temperature": 0.4
        }

    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    # Execute POST request synchronously
    with urllib.request.urlopen(req, timeout=10) as response:
        res_body = response.read().decode("utf-8")
        res_data = json.loads(res_body)
        
        candidates = res_data.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates returned from Gemini API.")
            
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise ValueError("No content parts returned from Gemini API.")
            
        text = parts[0].get("text", "")
        return text

def generate_coaching_response(prompt_text: str) -> MindShiftResponse:
    """
    Sends the coaching prompt to Gemini via raw HTTP request and parses the response
    into a MindShiftResponse Pydantic model.
    Retries once automatically on transient API/parsing failures, then falls back to local simulation.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        logger.warning("GEMINI_API_KEY not configured. Falling back to local empathetic engine.")
        return get_fallback_response(prompt_text)

    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        logger.info(f"Initiating HTTP call to Gemini. Attempt {attempt}/{max_attempts}.")
        start_time = time.time()
        try:
            raw_text = call_gemini_raw_http(prompt_text, is_json_response=True)
            duration = time.time() - start_time
            logger.info(f"Gemini raw HTTP call succeeded in {duration:.2f} seconds.")
            
            response_data = json.loads(raw_text)
            validated = MindShiftResponse.model_validate(response_data)
            return validated
        except Exception as e:
            logger.warning(f"HTTP Attempt {attempt}/{max_attempts} failed with: {str(e)}")
            if attempt == max_attempts:
                logger.error("All HTTP attempts failed. Launching local fallback handler.", exc_info=True)
                return get_fallback_response(prompt_text)
            time.sleep(1)

def generate_onboarding_plan(prompt_text: str) -> str:
    """
    Generates a 30-day recovery plan string from Gemini via HTTP request.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return get_fallback_onboarding_plan()
        
    try:
        plan_text = call_gemini_raw_http(prompt_text, is_json_response=False)
        if plan_text:
            return plan_text
        return get_fallback_onboarding_plan()
    except Exception as e:
        logger.error(f"Failed to generate onboarding plan via HTTP: {str(e)}")
        return get_fallback_onboarding_plan()

def generate_insight_response(prompt_text: str) -> str:
    """
    Generates weekly recovery insights using raw HTTP request to Gemini.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return "Your progress is steady. Continue logging check-ins to build awareness of your triggers."
        
    try:
        insight_text = call_gemini_raw_http(prompt_text, is_json_response=False)
        if insight_text:
            return insight_text.strip()
    except Exception as e:
        logger.error(f"Failed to generate weekly insight via HTTP: {str(e)}")
        
    return "Your progress is steady. You are logging check-ins and facing your triggers with high awareness. Keep moving one day at a time."

def get_fallback_response(prompt_text: str) -> MindShiftResponse:
    """
    Generates a realistic, empathetic offline fallback response to ensure 100% reliability.
    """
    lower_prompt = prompt_text.lower()
    
    # Heuristics matching triggers
    if "sos" in lower_prompt or "emergency" in lower_prompt:
        return MindShiftResponse(
            emotional_state="relapsing",
            coaching_persona="crisis",
            primary_message="I hear you, and I am glad you reached out. Take a deep breath right now. Close your eyes, exhale slowly, and put your device down for just 60 seconds. You are safe, and we can get through this trigger together.",
            micro_goal="Close your eyes and breathe deeply for 1 minute.",
            nudge_intensity="high",
            follow_up_prompt="How do you feel after taking that breath? Focus on the physical sensation.",
            flags=["relapse_risk"]
        )
    elif "relapse" in lower_prompt or "failed" in lower_prompt or "screwed up" in lower_prompt or "slip" in lower_prompt:
        return MindShiftResponse(
            emotional_state="relapsing",
            coaching_persona="crisis",
            primary_message="Please don't be discouraged. A relapse is just data, not a definition of who you are. We are keeping your streak count active as a 'Recovery Streak' because your past successful days still count. Let's focus on what we can do in the next hour.",
            micro_goal="Put your phone in another room for the next 30 minutes.",
            nudge_intensity="high",
            follow_up_prompt="What trigger was most active before this slip occurred? Was it stress, boredom, or something else?",
            flags=["relapse_risk"]
        )
    elif "stress" in lower_prompt or "anxious" in lower_prompt or "tired" in lower_prompt or "bored" in lower_prompt:
        return MindShiftResponse(
            emotional_state="stressed",
            coaching_persona="supportive",
            primary_message="It sounds like you're carrying a heavy load right now. When we feel stressed, our brains naturally look for a quick dopamine escape like doom-scrolling. Let's redirect that impulse to something gentle.",
            micro_goal="Do a quick 2-minute physical stretch right now.",
            nudge_intensity="medium",
            follow_up_prompt="Could you describe what's causing the stress? Just writing it down can help release its grip.",
            flags=[]
        )
    else:
        return MindShiftResponse(
            emotional_state="motivated",
            coaching_persona="supportive",
            primary_message="That is fantastic! Keeping your awareness high is the absolute key to recovery. You're doing wonderful work building these new mental pathways.",
            micro_goal="Enjoy 15 minutes of quiet time reading a physical book or looking out the window.",
            nudge_intensity="low",
            follow_up_prompt="What feel different about today compared to days when cravings are stronger?",
            flags=[]
        )

def get_fallback_onboarding_plan() -> str:
    return """# Your 30-Day MindShift Recovery Plan (Local Fallback Mode)

Welcome to your personalized recovery journey. Here is your roadmap for the next 30 days:

### Week 1 — Awareness & Grounding
*   **Focus**: Identify trigger moments and log your baseline screen times.
*   **Milestone**: Complete 5 days of check-ins without screen time overflows.

### Week 2 — Friction Building
*   **Focus**: Implement physical barriers (e.g. phone in drawer during work, grey-scale screen settings).
*   **Milestone**: Cut evening screen use by 30%.

### Week 3 — Alternative Rewards
*   **Focus**: Swap scroll sessions with high-quality real-world tasks (reading, walking, breathing exercises).
*   **Milestone**: Complete a 3-day recovery streak.

### Week 4 — Consolidation
*   **Focus**: Establish permanent triggers-response loops and consolidate your insights.
*   **Milestone**: Maintain a screen-time level matching your reduction goal.
"""
