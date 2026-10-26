from fastapi import FastAPI
from pydantic import BaseModel
from qloo_client import API_KEY
import db
from agent import ask
from fastapi.responses import FileResponse

app = FastAPI()
db.init_db()
db.seed_demo()


class Favourite(BaseModel):
    user_id: str = "demo"
    category: str  # music, movies, food, travel
    name: str


class Consent(BaseModel):
    user_id: str = "demo"
    category: str
    allowed: bool


class Ask(BaseModel):
    user_id: str = "demo"
    question: str
    use_passport: bool = True


@app.get("/health")
def health():
    return {"ok": True, "qloo_key_loaded": bool(API_KEY)}


@app.post("/favourites")
def add_favourite(f: Favourite):
    db.add_favourite(f.user_id, f.category, f.name)
    return {"saved": True}


@app.post("/consent")
def set_consent(c: Consent):
    db.set_consent(c.user_id, c.category, c.allowed)
    return {"saved": True}


@app.get("/profile/{user_id}")
def profile(user_id: str, only_allowed: bool = False):
    return {
        "favourites": db.get_favourites(user_id, only_allowed),
        "consent": db.get_consent(user_id),
    }


@app.post("/ask")
def ask_endpoint(a: Ask):
    return ask(a.user_id, a.question, a.use_passport)

@app.get("/")
def home():
    return FileResponse("static/index.html")