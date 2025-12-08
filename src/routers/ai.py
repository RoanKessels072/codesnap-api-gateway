from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.nats_client import nats_client
from src.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])

class FeedbackRequest(BaseModel):
    code: str
    language: str
    exercise_name: str
    exercise_description: str
    reference_solution: Optional[str] = ""

class RivalRequest(BaseModel):
    exercise_id: int
    exercise_name: str
    exercise_description: str
    difficulty: str
    language: str
    starter_code: Optional[str] = None
    function_name: str
    test_cases: list

@router.post("/assistant")
async def get_ai_feedback(
    request_data: FeedbackRequest, 
    user: dict = Depends(get_current_user)
):
    try:
        return await nats_client.request("ai.feedback", request_data.model_dump(), timeout=20)
    except TimeoutError:
        raise HTTPException(status_code=504, detail="AI Timeout")

@router.post("/rival")
async def generate_ai_rival(
    request_data: RivalRequest, 
    user: dict = Depends(get_current_user)
):
    try:
        return await nats_client.request("ai.rival", request_data.model_dump(), timeout=30)
    except TimeoutError:
        raise HTTPException(status_code=504, detail="AI Rival Timeout")