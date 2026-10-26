# Taste Passport

Your taste in one place. AI agents can read it only for the categories you allow.

Built for the Qloo Agentic Hackathon.

**Live demo:** https://taste-passport-3k1m.onrender.com
(Free hosting: the first load can take up to a minute while the server wakes up.)

## What it does
- You save a few favourites (music, movies, food, travel).
- You choose which categories an AI agent may see.
- The agent calls tools to read your passport and make recommendations.
- Consent is enforced inside the tools, so a blocked category never reaches the AI.
- A "Use my Taste Passport" switch shows the before/after: generic answer vs. taste-based answer.

## How it works
Browser -> FastAPI server -> AI agent (Gemini) -> tools (`get_taste_profile`, `recommend`) -> SQLite passport + consent layer.

## Run locally
    git clone https://github.com/aarati5/qloo-taste-agent.git
    cd qloo-taste-agent
    python -m venv venv
    venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
    pip install -r requirements.txt

Create a `.env` file:

    GEMINI_API_KEY=your_key
    QLOO_API_KEY=your_key

Start the server and open http://127.0.0.1:8000

    uvicorn main:app --reload

## Tech
Python, FastAPI, SQLite, Google Gemini API, Qloo API.

## License
MIT