import os
import time
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config before any other Streamlit command
st.set_page_config(
    page_title="MindShift — AI Recovery Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.database import init_db, get_profile, get_streak, get_recent_logs, update_streak, clear_db
from src.validators import validate_profile_input, validate_screen_time
from src.planner import onboard_user, process_checkin, process_relapse, generate_weekly_insight
from src.utils import setup_logging, get_logger, get_gemini_api_key

# Initialize DB and Logging
init_db()
logger = setup_logging()

# ==========================================
# Custom CSS for Premium Design & Animation
# ==========================================
@st.cache_data
def get_custom_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Background blob styling */
    .stApp {
        background-color: #080d0a;
        background-image: 
            radial-gradient(at 10% 20%, rgba(46, 204, 113, 0.05) 0px, transparent 50%),
            radial-gradient(at 90% 80%, rgba(241, 196, 15, 0.03) 0px, transparent 50%);
    }

    /* Glassmorphic Container styling */
    .glass-card {
        background: rgba(15, 25, 20, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(46, 204, 113, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .glass-card:hover {
        border-color: rgba(46, 204, 113, 0.35);
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #09120c 0%, #0d2012 100%);
        border: 1px solid rgba(46, 204, 113, 0.25);
        padding: 30px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }
    .header-title {
        font-weight: 800;
        background: linear-gradient(90deg, #2ecc71 0%, #1abc9c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        margin: 0;
        letter-spacing: 1.5px;
    }
    .header-subtitle {
        color: #d5ded9;
        font-size: 1.1rem;
        margin-top: 8px;
        font-weight: 400;
    }
    
    /* Input placeholder accessibility override */
    ::placeholder {
        color: #8b9e95 !important;
        opacity: 1 !important;
    }
    
    /* Streak Badge widget styling */
    .streak-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .streak-badge-habit {
        background: rgba(46, 204, 113, 0.1);
        border: 1px solid rgba(46, 204, 113, 0.4);
        color: #2ecc71;
        box-shadow: 0 0 15px rgba(46, 204, 113, 0.2);
    }
    
    .streak-badge-recovery {
        background: rgba(241, 196, 15, 0.1);
        border: 1px solid rgba(241, 196, 15, 0.4);
        color: #f1c40f;
        box-shadow: 0 0 15px rgba(241, 196, 15, 0.2);
    }
    
    /* Emergency SOS Button styling */
    .sos-btn-container {
        text-align: center;
        margin-top: 15px;
    }
    
    .sos-active-banner {
        background: rgba(231, 76, 60, 0.15);
        border: 1px solid rgba(231, 76, 60, 0.4);
        color: #e74c3c;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        animation: pulseSOS 2s infinite alternate;
        margin-bottom: 20px;
    }
    
    @keyframes pulseSOS {
        0% { box-shadow: 0 0 5px rgba(231, 76, 60, 0.2); }
        100% { box-shadow: 0 0 20px rgba(231, 76, 60, 0.5); }
    }
    
    /* Debug Pane styling */
    .debug-pane {
        background-color: #050806;
        border: 1px solid #112217;
        font-family: 'Courier New', Courier, monospace;
        color: #4ef08f;
        padding: 15px;
        border-radius: 8px;
        max-height: 300px;
        overflow-y: auto;
        font-size: 0.85rem;
    }
    
    /* Typography improvements */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
    }
    
    /* Metric Card styling */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2ecc71;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #c5d0ca;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Style Streamlit Input Widgets */
    div[data-baseweb="input"] {
        background-color: rgba(5, 10, 7, 0.6) !important;
        border: 1px solid rgba(46, 204, 113, 0.25) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        color: #f0f5f2 !important;
    }
    div[data-baseweb="select"] {
        background-color: rgba(5, 10, 7, 0.6) !important;
        border: 1px solid rgba(46, 204, 113, 0.25) !important;
        border-radius: 8px !important;
    }
    
    /* Primary buttons (e.g. SOS Button) */
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: 1px solid rgba(231, 76, 60, 0.4) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
    }
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.6) !important;
    }

    /* Secondary / Form buttons (e.g. Submissions, Nudges) */
    button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #2ecc71 0%, #1abc9c 100%) !important;
        color: #080d0a !important;
        font-weight: 700 !important;
        border: 1px solid rgba(46, 204, 113, 0.3) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.2) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(46, 204, 113, 0.5) !important;
        color: #ffffff !important;
    }

    /* Danger zone reset button or sidebar overrides */
    [data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #a3b3aa !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
        background: rgba(231, 76, 60, 0.15) !important;
        color: #e74c3c !important;
        border-color: rgba(231, 76, 60, 0.3) !important;
    }
    </style>
    """

st.markdown(get_custom_css(), unsafe_allow_html=True)

# Helper function to simulate streaming of text
def stream_text(text: str, delay: float = 0.01):
    """
    Renders text character-by-character to simulate dynamic streaming.
    """
    placeholder = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        placeholder.markdown(full_text + "▌")
        time.sleep(delay)
    placeholder.markdown(text)

# Initialize Session State
if "active_response" not in st.session_state:
    st.session_state.active_response = None
if "onboarding_plan" not in st.session_state:
    st.session_state.onboarding_plan = None
if "sos_mode" not in st.session_state:
    st.session_state.sos_mode = False
if "simulated_nudge" not in st.session_state:
    st.session_state.simulated_nudge = None
if "last_action" not in st.session_state:
    st.session_state.last_action = None
if "needs_streaming" not in st.session_state:
    st.session_state.needs_streaming = False

# Sidebar Content
with st.sidebar:
    st.subheader("⚙️ System Controls")
    
    # API Configuration Check
    api_key = get_gemini_api_key()
    if api_key:
        st.success("🔑 Gemini API Key configured.")
    else:
        st.error("⚠️ GEMINI_API_KEY is not set.")
        manual_key = st.text_input("Enter Gemini API Key", type="password", help="Paste your Google Gemini API Key here to enable live AI responses.")
        if manual_key:
            os.environ["GEMINI_API_KEY"] = manual_key
            st.success("API key applied for this session!")
            st.rerun()

    # Reset System Option
    st.markdown("---")
    st.subheader("⚠️ Danger Zone")
    if st.button("Reset All Companion Data", use_container_width=True, help="Warning: This will permanently delete all logs, streaks, and your profile data."):
        clear_db()
        st.session_state.clear()
        st.success("All data cleared. Restarting companion onboarding!")
        time.sleep(1)
        st.rerun()

# Check if User Profile exists in Database
profile = get_profile()

if not profile:
    # ==========================================
    # ONBOARDING VIEW (Phase 1)
    # ==========================================
    st.markdown('<div class="header-card" role="banner"><h1 class="header-title">MIND<span>SHIFT</span></h1><p class="header-subtitle">AI-Powered Recovery Companion for Digital Addictions</p></div>', unsafe_allow_html=True)
    
    st.markdown("## Welcome to your MindShift Onboarding")
    st.markdown("Before we can build your recovery companion, let's configure your journey.")
    
    with st.form("onboarding_form"):
        habit = st.selectbox(
            "Select the digital addiction you wish to recover from:",
            ["Doom-scrolling (TikTok/Instagram Reels)", "Excessive Social Media checking", "Compulsive mobile gaming", "Late-night screen browsing", "Online news micro-obsessions"],
            help="Choose the digital behavioral pattern you want to recover from."
        )
        
        triggers = st.text_input(
            "What triggers this behavior? (Comma-separated, e.g. stress, boredom, morning waking):",
            placeholder="boredom, morning waking, study stress",
            help="List any emotional states, environments, or schedules that prompt this behavior."
        )
        
        goal = st.text_input(
            "What is your target screen time goal? (e.g. Reduce from 8hrs to 3hrs daily):",
            placeholder="Reduce from 6hrs to 2hrs daily",
            help="Specify your target daily screen time limit."
        )
        
        submit_btn = st.form_submit_button("Generate My Recovery Plan", use_container_width=True)
        
        if submit_btn:
            is_valid, err_msg, profile_input = validate_profile_input(habit, triggers, goal)
            if not is_valid:
                st.error(err_msg)
            else:
                with st.spinner("🧠 Establishing neural-reframe strategies and generating your recovery plan..."):
                    try:
                        plan_text = onboard_user(profile_input)
                        st.session_state.onboarding_plan = plan_text
                        st.success("Onboarding Plan generated successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed during onboarding: {str(e)}")

else:
    # ==========================================
    # DASHBOARD VIEW (Phases 2-4)
    # ==========================================
    
    # Read state parameters
    streak = get_streak()
    recent_logs = get_recent_logs(limit=5)
    
    # Custom Header
    st.markdown('<div class="header-card" role="banner"><h1 class="header-title">MIND<span>SHIFT</span></h1><p class="header-subtitle">Recovery Companion &middot; Dynamic Coaching Dashboard</p></div>', unsafe_allow_html=True)
    
    # Layout Grid: Left pane (Streak, SOS, Check-in) | Right pane (Timeline, Analytics, Insights)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 1. Streak Widget (Phase 3)
        streak_style = "streak-badge-recovery" if streak["type"] == "recovery" else "streak-badge-habit"
        streak_name = "Recovery Streak" if streak["type"] == "recovery" else "Clean Habit Streak"
        
        st.markdown(f"""
        <div class="streak-container {streak_style}" role="status" aria-live="polite" aria-label="{streak_name}: {streak['count']} Days">
            <i class="fa-solid fa-fire-flame-simple" style="font-size: 2rem;" role="img" aria-hidden="true"></i>
            <div>
                <div class="metric-value" style="color: inherit;">{streak['count']} Days</div>
                <div class="metric-label" style="color: inherit;">{streak_name}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Emergency SOS Widget (Phase 4)
        if st.session_state.sos_mode:
            st.markdown('<div class="sos-active-banner" role="alert"><i class="fa-solid fa-circle-exclamation" role="img" aria-hidden="true"></i> EMERGENCY SOS MODE ACTIVE &middot; AI COACH RESPONDING IN CRISIS PERSONA</div>', unsafe_allow_html=True)
            if st.button("Cancel Crisis SOS Mode", type="secondary", use_container_width=True):
                st.session_state.sos_mode = False
                st.rerun()
        else:
            if st.button("🚨 Emergency SOS Trigger", type="primary", use_container_width=True):
                st.session_state.sos_mode = True
                st.session_state.last_action = "sos"
                st.rerun()
        
        # 3. Main Input Panel (Check-in or Relapse)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        if st.session_state.sos_mode:
            st.subheader("🔥 Immediate Crisis Support")
            st.write("Tell your coach what triggers are pulling you to the screen right now. We will help you ground yourself.")
            
            with st.form("sos_form"):
                user_msg = st.text_area("Tell us what's happening:", height=100, placeholder="I am staring at my phone and have a strong urge to open social media...", help="Describe what is triggering your urge so the coach can offer immediate grounding techniques.")
                sos_submit = st.form_submit_button("Request Crisis Intervention")
                
                if sos_submit:
                    if not user_msg.strip():
                        st.error("Please enter what is happening so the coach can assist.")
                    else:
                        with st.spinner("AI Coach entering crisis-intervention mode..."):
                            try:
                                response = process_relapse(f"SOS CRISIS TRIGGERED: {user_msg}")
                                st.session_state.active_response = response.model_dump()
                                st.session_state.last_action = "response"
                                st.session_state.needs_streaming = True
                                st.rerun()
                            except Exception as e:
                                st.error(f"SOS Intervention call failed: {str(e)}")
                                
        elif st.session_state.last_action == "nudge":
            st.subheader("🔔 Trigger Nudge Simulation")
            st.warning(f"**Nudge Sent**: \"{st.session_state.simulated_nudge['primary_message']}\"")
            st.write("Respond to your coach's nudge below to check-in:")
            
            with st.form("nudge_response_form"):
                nudge_input = st.text_area("Your response:", height=100, placeholder="It's 2 PM and I am indeed feeling bored. I opened TikTok for a second but closed it.", help="Write how you are feeling or responding to the coach's nudge warning.")
                nudge_submit = st.form_submit_button("Send Response")
                
                if nudge_submit:
                    if not nudge_input.strip():
                        st.error("Please enter a response.")
                    else:
                        with st.spinner("Processing nudge response..."):
                            try:
                                response = process_checkin(nudge_input)
                                st.session_state.active_response = response.model_dump()
                                st.session_state.last_action = "response"
                                st.session_state.needs_streaming = True
                                st.session_state.simulated_nudge = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to process check-in: {str(e)}")
                                
        else:
            # Normal Daily Check-in / Relapse Log
            tabs = st.tabs(["Daily AI Check-in", "Log a Relapse / Bad Day"])
            
            with tabs[0]:
                st.write("Log your emotional check-in to receive today's micro-goal and keep your streak.")
                with st.form("checkin_form"):
                    checkin_msg = st.text_area("How are you feeling about your screen use today?", height=100, placeholder="I feel motivated. Kept phone away during lunch but felt a bit of an urge around 3pm...", help="Type down your physical/emotional checks, focus stats, or cravings.")
                    screen_time = st.number_input("Log actual screen time logged today (minutes, optional):", min_value=0, value=0, help="Optional. Enter the total screen time tracked in minutes today.")
                    
                    checkin_submit = st.form_submit_button("Submit Check-in")
                    
                    if checkin_submit:
                        if not checkin_msg.strip():
                            st.error("Please type your check-in notes.")
                        else:
                            with st.spinner("AI Coach analyzing check-in and emotional state..."):
                                try:
                                    response = process_checkin(checkin_msg, actual_screen_time=screen_time)
                                    st.session_state.active_response = response.model_dump()
                                    st.session_state.last_action = "response"
                                    st.session_state.needs_streaming = True
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Check-in failed: {str(e)}")
                                    
            with tabs[1]:
                st.write("Logging a relapse handles your emotions compassionately. Your streak will be converted to a **Recovery Streak** rather than wiped out.")
                with st.form("relapse_form"):
                    relapse_msg = st.text_area("What trigger pulled you back to doom-scrolling?", height=100, placeholder="I got highly stressed about a work deadline and ended up doom-scrolling for 2 hours in the afternoon...", help="Describe what happened so the coach can adjust your roadmap without wiping your streak count.")
                    relapse_submit = st.form_submit_button("Report Relapse & Enter Recovery Mode")
                    
                    if relapse_submit:
                        if not relapse_msg.strip():
                            st.error("Please describe what happened so we can adjust your plan.")
                        else:
                            with st.spinner("AI Coach establishing relapse recovery strategies..."):
                                try:
                                    response = process_relapse(relapse_msg)
                                    st.session_state.active_response = response.model_dump()
                                    st.session_state.last_action = "response"
                                    st.session_state.needs_streaming = True
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Relapse logging failed: {str(e)}")
                                    
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 4. Scheduled Nudge Simulator Widget (Phase 2/4)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⏰ Nudge & Time Scheduler")
        st.write("In production, MindShift triggers context-aware nudges at high-risk times. Simulate a nudge right now:")
        if st.button("Simulate Context-Aware Nudge", use_container_width=True):
            with st.spinner("Generating nudge based on profile triggers & emotional states..."):
                try:
                    from src.prompts import NUDGE_PROMPT
                    from src.gemini import generate_coaching_response
                    
                    triggers_str = ", ".join(profile["declared_triggers"])
                    last_log = recent_logs[0] if recent_logs else None
                    active_goal = last_log["micro_goal_delivered"] if last_log else "Put phone away during work"
                    last_state = last_log["emotional_state_detected"] if last_log else "calm"
                    is_rel_active = "true" if streak["type"] == "recovery" else "false"
                    
                    nudge_prompt = NUDGE_PROMPT.format(
                        habit_type=profile["habit_type"],
                        triggers_str=triggers_str,
                        active_micro_goal=active_goal,
                        current_time="02:00 PM (High-Risk Peak)",
                        streak_count=streak["count"],
                        last_emotional_state=last_state,
                        is_relapse_active=is_rel_active
                    )
                    
                    nudge_response = generate_coaching_response(nudge_prompt)
                    st.session_state.simulated_nudge = nudge_response.model_dump()
                    st.session_state.last_action = "nudge"
                    st.rerun()
                except Exception as e:
                    st.error(f"Nudge simulation failed: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # ==========================================
        # AI Response Area (Phase 2/4)
        # ==========================================
        if st.session_state.last_action == "response" and st.session_state.active_response:
            st.markdown('<div class="glass-card" style="border-color: rgba(46, 204, 113, 0.45);">', unsafe_allow_html=True)
            st.subheader("💬 AI Coach Response")
            
            resp = st.session_state.active_response
            
            # Show Detected Status Indicators
            col_ind1, col_ind2, col_ind3 = st.columns(3)
            with col_ind1:
                st.markdown(f"**State**: `{resp['emotional_state'].upper()}`")
            with col_ind2:
                st.markdown(f"**Persona**: `{resp['coaching_persona'].upper()}`")
            with col_ind3:
                st.markdown(f"**Intensity**: `{resp['nudge_intensity'].upper()}`")
            
            # Animate the message text
            st.markdown("**Coach message:**")
            if st.session_state.get("needs_streaming", False):
                stream_text(resp["primary_message"])
                st.session_state.needs_streaming = False
            else:
                st.markdown(resp["primary_message"])
            
            # Highlight Micro-Goal
            goal_html = f"""
            <div style="background-color: rgba(46, 204, 113, 0.1); border-left: 4px solid #2ecc71; padding: 15px; border-radius: 8px; margin: 15px 0;" role="region" aria-label="Today's Micro Goal">
                <strong style="color: #2ecc71; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px;">Today&apos;s Micro-Goal:</strong>
                <p style="font-size: 1.15rem; font-weight: 600; margin: 5px 0 0 0;">{resp["micro_goal"]}</p>
            </div>
            """
            st.markdown(goal_html, unsafe_allow_html=True)
            
            st.markdown(f"*Prompt: {resp['follow_up_prompt']}*")
            
            # Check for flags and display alerts
            for flag in resp["flags"]:
                if flag == "relapse_risk":
                    st.error("🚨 Relapse Risk flag detected. Relapse support protocols loaded.")
                elif flag == "milestone_reached":
                    st.success("🎉 Celebration Milestone reached! Keep climbing!")
                elif flag == "pattern_detected":
                    st.warning("⚠️ Behavioral trigger pattern identified by coach.")
            
            # Expose Judge Live JSON Debugger Panel (Phase 4)
            st.markdown("---")
            with st.expander("🛠️ PromptWars Live JSON Debugger (Scoring Board)", expanded=True):
                st.markdown("Judges can inspect the exact structured JSON response returned from the Gemini API:")
                st.json(resp)
                
            if st.button("Close Response", use_container_width=True):
                st.session_state.last_action = None
                st.session_state.active_response = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # 5. Weekly AI Insights & Dashboard (Phase 3)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Weekly AI Analysis")
        
        # Interactive Generation of Insights
        if st.button("Generate Weekly Analytical Summary", use_container_width=True):
            with st.spinner("Aggregating historical session logs and patterns..."):
                insight_narrative = generate_weekly_insight()
                st.info(insight_narrative)
        else:
            st.write("Click above to compile your logs into a custom, non-judgmental AI narrative summary.")
            
        st.markdown('</div>', unsafe_allow_html=True)

        # 6. Active Recovery Plan (Phase 1)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📅 Your 30-Day MindShift Roadmap")
        with st.expander("View Active 30-Day Plan Detail", expanded=True):
            st.markdown(profile["thirty_day_plan"])
        st.markdown('</div>', unsafe_allow_html=True)

        # 7. Interaction Log Feed
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📜 Recent Companion Activity Feed")
        if recent_logs:
            for log in recent_logs:
                log_time = datetime = log["timestamp"][:16].replace("T", " ")
                log_icon = "🚨" if log["session_type"] == "relapse" else "checkin"
                st.markdown(f"**[{log_time}] {log['session_type'].upper()} check-in**")
                st.write(f"*User: \"{log['user_input_text']}\"*")
                st.write(f"*AI Response: \"{log['micro_goal_delivered']}\"*")
                st.markdown("---")
        else:
            st.write("No session records found. Log your first check-in to populate the feed!")
        st.markdown('</div>', unsafe_allow_html=True)
