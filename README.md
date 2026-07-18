# MindShift: AI Recovery Companion for Digital Addictions

MindShift is a production-ready AI companion and digital recovery assistant designed for PromptWars Hyderabad. It targets excessive screen time, doom-scrolling, and digital compulsions. By combining behavioral science (CBT, relapse intervention) with real-time generative AI, MindShift replaces static habit logs with an empathetic, context-aware AI coach.

---

## 🚀 Features

- **Personalized Onboarding**: Builds tailored 30-day recovery plans and milestones based on user habits and declared triggers.
- **Adaptive Daily AI Coaching**: Analyzes free-text check-ins to detect emotional states (stressed, anxious, motivated, calm, relapsing), selects matching coaching personas (supportive, firm, celebratory, crisis), and issues a daily micro-goal.
- **Intelligent Context-Aware Nudge System**: Dynamically generates and schedules personalized nudges based on high-risk triggers and previous logs.
- **Empathetic Relapse Recovery Loop**: Supports bad days with a dedicated Recovery Mode. Instead of wiping streaks to zero, it converts them into a glowing **"Recovery Streak"** to preserve user motivation.
- **Weekly Insight Narratives**: Compiles recent check-ins and trigger logs into descriptive paragraph summaries detailing behavioral patterns.
- **Judge Dev/Debug Panel**: Displays raw, structured JSON response payloads from Gemini for judging scoring verification.

---

## 🛠️ Tech Stack & Technologies Used

- **Frontend**: [Streamlit](https://streamlit.io/) (v1.35.0+)
- **AI Integration**: Raw REST HTTP POST calls directly to Google's Gemini API endpoints calling `gemini-2.5-flash` (using Python's standard library `urllib` — **zero GenAI SDK dependency**)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/latest/) (v2.7.0+)
- **Database**: **SQLite** (standard library `sqlite3` - zero infrastructure configuration)
- **Testing**: `pytest` (v8.0.0+)

---

## 📂 Project Structure

```
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── app.py              # Main Streamlit dashboard interface
├── src/
│   ├── __init__.py
│   ├── gemini.py       # Raw HTTP Gemini API integration, retry, and offline fallbacks
│   ├── planner.py      # Planner orchestrator (check-ins, relapse, streaks, insights)
│   ├── database.py     # SQLite schema, profile persistence, and logs
│   ├── prompts.py      # Structured system instructions & prompt templates
│   ├── models.py       # Pydantic schemas (MindShiftResponse, UserProfileInput)
│   ├── validators.py   # Input checks and sanitization rules
│   └── utils.py        # Helpers (logging, key resolution, key verification)
└── tests/
    ├── __init__.py
    ├── test_validators.py   # Unit tests for profile and screen time validators
    └── test_budget.py       # Unit tests for database logs and streak records
```

---

## 🤖 How Gemini is Used

MindShift integrates structured GenAI calls via raw HTTP POSTs to the REST API:
1. **Schema Enforcement**: Injects `responseMimeType="application/json"` and `responseSchema` directly in the HTTP payload config.
2. **Context Injection**: Automatically query SQLite to load recent session histories and insert them into the prompts, preventing robotic one-off replies.
3. **API Key Fallback**: Catches API timeouts or missing keys, routing to a realistic mock data generator to guarantee continuous runtime reliability.

---

## ⚡ Local Setup & Run

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your `GEMINI_API_KEY`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(If you do not set it in `.env`, you can paste it directly in the application's sidebar at runtime).*

### 4. Start the Application
Run the Streamlit server:
```bash
streamlit run app.py
```

---

## ☁️ Render Deployment

MindShift is optimized for hosting on **Render**:
1. Connect your GitHub repository to [Render](https://render.com/).
2. Create a new **Web Service** with the configuration:
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3. Under **Advanced Settings**, add the environment secret:
   * `GEMINI_API_KEY` = `your_actual_gemini_api_key_here`
4. Click **Create Web Service**. Dependencies will build and deploy on a permanent static URL.
