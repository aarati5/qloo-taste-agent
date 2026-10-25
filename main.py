from fastapi import FastAPI
from qloo_client import API_KEY

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True, "qloo_key_loaded": bool(API_KEY)}