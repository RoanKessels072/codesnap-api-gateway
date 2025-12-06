from fastapi import APIRouter, Depends
from src.nats_client import nats_client
from src.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/assistant")
async def get_ai_feedback(data: dict, user: dict = Depends(get_current_user)):
    return await nats_client.request("ai.feedback", data)

@router.post("/rival")
async def generate_ai_rival(data: dict, user: dict = Depends(get_current_user)):
    return await nats_client.request("ai.rival", data)