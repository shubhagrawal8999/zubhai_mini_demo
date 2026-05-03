from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from supabase import create_client, Client
import os

app = FastAPI(title="Zubhai API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


class SelectSkillRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    skill: str = Field(..., min_length=1)


@app.post("/select-skill")
def select_skill(payload: SelectSkillRequest):
    try:
        result = (
            supabase
            .table("users")
            .update({"selected_skill": payload.skill})
            .eq("id", payload.user_id)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save skill: {exc}")

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "ok": True,
        "user_id": payload.user_id,
        "selected_skill": payload.skill,
    }
