import os
import httpx
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://hackathon.api.qloo.com"
API_KEY = os.getenv("QLOO_API_KEY", "")


def qloo_get(path: str, params: dict) -> dict:
    """Calls Qloo. Returns {} if no key yet (demo mode)."""
    if not API_KEY:
        return {}
    r = httpx.get(
        BASE_URL + path,
        params=params,
        headers={"X-Api-Key": API_KEY},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()