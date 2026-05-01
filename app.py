import json
import os
import re
from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Zubhai API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")


class OnboardRequest(BaseModel):
    user_id: str = Field(min_length=3)
    answers: List[str] = Field(min_length=5, max_length=5)


class ChallengeRequest(BaseModel):
    user_id: str


class GradeRequest(BaseModel):
    user_id: str
    submission: str = Field(min_length=5)


def extract_json_block(raw: str) -> Dict[str, Any]:
    if not raw:
        return {}
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


async def supabase_request(method: str, path: str, payload: Dict[str, Any] | None = None, query: str = "") -> Any:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise HTTPException(status_code=500, detail="Supabase is not configured")
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{SUPABASE_URL}/rest/v1/{path}{query}"
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.request(method, url, headers=headers, json=payload)
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Supabase error: {response.text}")
    if not response.text:
        return None
    return response.json()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/state/{user_id}")
async def get_state(user_id: str) -> Dict[str, Any]:
    data = await supabase_request("GET", "profiles", query=f"?id=eq.{user_id}&select=*")
    if not data:
        return {"user_id": user_id, "onboarding_complete": False, "current_day": 1, "total_points": 0}
    return data[0]


@app.post("/onboard")
async def onboard(req: OnboardRequest) -> Dict[str, Any]:
    profile = {
        "id": req.user_id,
        "field": req.answers[0],
        "level": req.answers[1],
        "goals": req.answers[2],
        "language": req.answers[3],
        "time_commitment": req.answers[4],
        "onboarding_complete": True,
        "current_day": 1,
        "total_points": 0,
    }
    await supabase_request("POST", "profiles", payload=profile, query="?on_conflict=id")
    return {"ok": True, "profile": profile}


@app.post("/generate-challenge")
async def generate_challenge(req: ChallengeRequest) -> Dict[str, Any]:
    state = await get_state(req.user_id)
    challenge = (
        f"Day {state['current_day']} challenge for {state.get('field','general')} ({state.get('level','beginner')}): "
        f"Build a practical AI workflow and explain your prompt strategy in {state.get('language','English')}."
    )
    return {"challenge": challenge, "current_day": state["current_day"]}


@app.post("/grade")
async def grade(req: GradeRequest) -> Dict[str, Any]:
    state = await get_state(req.user_id)
    base_score = min(10, max(1, len(req.submission) // 80 + 4))
    feedback = "Good attempt. Add clearer outcomes, metrics, and prompt iteration details."
    result = {"score": base_score, "feedback": feedback}

    score = int(result.get("score", 1)) if isinstance(result.get("score", 1), int) else 1
    score = min(10, max(1, score))
    gained = score * 10
    new_points = int(state.get("total_points", 0)) + gained
    new_day = min(21, int(state.get("current_day", 1)) + 1)

    await supabase_request(
        "PATCH",
        "profiles",
        payload={"total_points": new_points, "current_day": new_day},
        query=f"?id=eq.{req.user_id}",
    )

    return {
        "score": score,
        "feedback": result.get("feedback", feedback),
        "points_gained": gained,
        "total_points": new_points,
        "current_day": new_day,
    }


@app.get("/leaderboard")
async def leaderboard() -> Dict[str, Any]:
    rows = await supabase_request("GET", "profiles", query="?select=id,field,total_points,current_day&order=total_points.desc&limit=10")
    return {"top": rows or []}
