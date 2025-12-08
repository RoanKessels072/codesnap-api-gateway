from fastapi import APIRouter, Depends, HTTPException
from src.nats_client import nats_client
from src.auth import get_current_user

router = APIRouter(prefix="/attempts", tags=["Attempts"])

@router.post("/")
async def submit_attempt(data: dict, user: dict = Depends(get_current_user)):
    exercise_id = None
    code = data.get("code")

    if "exercise_id" in data:
        exercise_id = data["exercise_id"]
    elif "id" in data:
        exercise_id = data["id"]
    elif "exercise" in data and isinstance(data["exercise"], dict):
        exercise_id = data["exercise"].get("id")
    
    if not exercise_id:
        raise HTTPException(status_code=400, detail="Missing required field: exercise_id")
    if not code:
        raise HTTPException(status_code=400, detail="Missing required field: code")

    user_resp = await nats_client.request("users.get", {"keycloak_id": user["keycloak_id"]})
    
    if "error" in user_resp:
        print(f"User {user.get('username')} not found. Auto-creating...")
        create_payload = {
            "keycloak_id": user["keycloak_id"],
            "username": user.get("username", "unknown")
        }
        user_resp = await nats_client.request("users.create", create_payload)
        
        if "error" in user_resp:
             raise HTTPException(status_code=500, detail=f"Failed to create user: {user_resp['error']}")

    exercise_resp = await nats_client.request("exercises.get", {"id": exercise_id})
    
    if "error" in exercise_resp:
        raise HTTPException(status_code=404, detail=f"Exercise not found: {exercise_resp['error']}")

    payload = {
        "user_id": user_resp["id"],
        "exercise_id": exercise_id,
        "code": code,
        "language": exercise_resp.get("language"),
        "function_name": exercise_resp.get("function_name"),
        "test_cases": exercise_resp.get("test_cases")
    }
    
    if not payload["test_cases"] or not payload["language"]:
         raise HTTPException(status_code=500, detail="Exercise configuration is incomplete (missing tests or language)")

    response = await nats_client.request("attempts.create", payload, timeout=20.0)
    
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
        
    return response

@router.get("/my-history")
async def get_my_attempts(user: dict = Depends(get_current_user)):
    user_resp = await nats_client.request("users.get", {"keycloak_id": user["keycloak_id"]})
    if "error" in user_resp:
        return []
        
    return await nats_client.request("attempts.user", {"user_id": user_resp["id"]})

@router.get("/best")
async def get_best_attempts(user: dict = Depends(get_current_user)):
    user_resp = await nats_client.request("users.get", {"keycloak_id": user["keycloak_id"]})
    if "error" in user_resp:
        return {}
        
    response = await nats_client.request("attempts.best.all", {"user_id": user_resp["id"]})
    
    if "error" in response:
        return {}
    
    return response