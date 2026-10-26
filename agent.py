import time
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import db
from qloo_client import API_KEY as QLOO_KEY

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=20000),
)
MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]

SYSTEM = (
    "You are a personal assistant with access to the user's Taste Passport. "
    "First call get_taste_profile. Then call recommend for each relevant category. "
    "Use only what the tools return and explain briefly why each pick fits the user. "
    "If a tool says a category is not allowed, do not guess that category; "
    "tell the user you don't have access to it."
    "Reply in plain text only. No markdown, no asterisks, no # headings. "
    "Use short lines starting with a dash for lists."
)

# TEMPORARY demo data, used only until the Qloo key arrives
DEMO_RECS = {
    "music": ["Portishead", "Massive Attack", "Bon Iver"],
    "food": ["Filter coffee cafe", "Hyderabadi biryani house", "Ramen bar"],
    "movies": ["Her", "Arrival", "Eternal Sunshine of the Spotless Mind"],
    "travel": ["Hampi", "Gokarna", "Palolem Beach"],
}


def make_tools(user_id: str, trace: list):
    def get_taste_profile() -> dict:
        """Returns the user's saved favourites, only for categories the user has allowed."""
        trace.append("get_taste_profile()")
        favs = db.get_favourites(user_id, only_allowed=True)
        return {"favourites": [{"category": f["category"], "name": f["name"]} for f in favs]}

    def recommend(category: str, city: str = "") -> dict:
        """Taste-matched recommendations for one category (music, food, movies or travel). City is optional."""
        trace.append(f"recommend({category}, {city})")
        consent = db.get_consent(user_id)
        if consent.get(category, True) is False:
            return {"error": f"The user has not allowed access to '{category}'."}
        favs = [f["name"] for f in db.get_favourites(user_id, only_allowed=True)
                if f["category"] == category]
        items = DEMO_RECS.get(category, [])
        base = favs[0] if favs else "your saved taste"
        return {
            "source": "demo-data",
            "items": [{"name": n, "why": f"Similar in mood to {base}"} for n in items],
        }

    return [get_taste_profile, recommend]


def ask(user_id: str, question: str, use_passport: bool = True) -> dict:
    trace = []
    if use_passport:
        config = types.GenerateContentConfig(
            tools=make_tools(user_id, trace), system_instruction=SYSTEM
        )
    else:
        config = types.GenerateContentConfig(
            system_instruction="Answer helpfully. You know nothing about the user's personal tastes."
        )

    last_error = ""
    for model in MODELS:
        for attempt in range(1):
            trace.clear()
            try:
                resp = client.models.generate_content(
                    model=model, contents=question, config=config
                )
                return {
                    "answer": resp.text,
                    "trace": trace,
                    "used_passport": use_passport,
                    "model": model,
                }
            except Exception as e:
                last_error = str(e)
                busy = any(k in last_error for k in ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"))
                if busy:
                    time.sleep(1)
                    continue
                break  # other errors (e.g. 404): try next model

    return {
        "answer": "The AI is busy right now. Please try again in a minute.",
        "trace": [],
        "error": last_error,
    }