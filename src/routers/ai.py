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
    code: str #This is the users code to be graded alongside the rival

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
    print(f"DEBUG_GATEWAY: Received rival request for {request_data.exercise_name}", flush=True)
    
    try:
        user_resp = await nats_client.request("users.get", {"keycloak_id": user["keycloak_id"]})
        if "error" in user_resp:
            create_payload = {
                "keycloak_id": user["keycloak_id"],
                "username": user.get("username", "unknown")
            }
            user_resp = await nats_client.request("users.create", create_payload)
            if "error" in user_resp:
                 raise HTTPException(status_code=500, detail=f"Failed to create user: {user_resp['error']}")

        user_attempt_payload = {
            "user_id": user_resp["id"],
            "exercise_id": request_data.exercise_id,
            "code": request_data.code,
            "language": request_data.language,
            "function_name": request_data.function_name,
            "test_cases": request_data.test_cases
        }
        
        print("DEBUG_GATEWAY: Submitting user attempt...", flush=True)
        user_attempt_resp = await nats_client.request("attempts.create", user_attempt_payload, timeout=10.0)
        
        ai_payload = request_data.model_dump(exclude={"code"})
        
        print("DEBUG_GATEWAY: Requesting AI Rival...", flush=True)
        ai_resp = await nats_client.request("ai.rival", ai_payload, timeout=30.0)

        response = {
            "user_attempt": user_attempt_resp,
            "ai_rival": ai_resp
        }
        
        print(f"DEBUG_GATEWAY: Combined response generated.", flush=True)
        return response

    except TimeoutError:
        print("DEBUG_GATEWAY: Timeout handling rival request", flush=True)
        raise HTTPException(status_code=504, detail="Timeout processing rival request")
    except Exception as e:
        print(f"DEBUG_GATEWAY: Unexpected error: {e}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))