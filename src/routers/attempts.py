from fastapi import APIRouter, Depends
from src.nats_client import nats_client
from src.auth import get_current_user

router = APIRouter(prefix="/attempts", tags=["Attempts"])

@router.post("/")
async def submit_attempt(data: dict, user: dict = Depends(get_current_user)):    
    user_resp = await nats_client.request("users.get", {"keycloak_id": user["keycloak_id"]})
    if "error" in user_resp:
        return {"error": "User not initialized"}
        
    payload = {
        **data,
        "user_id": user_resp["id"] 
    }
    
    return await nats_client.request("attempts.create", payload)

@router.get("/my-history")
async def get_my_attempts(user: dict = Depends(get_current_user)):
    user_resp = await nats_client.request("users.get", {"keycloak_id": user["keycloak_id"]})
    if "error" in user_resp:
        return []
        
    return await nats_client.request("attempts.user", {"user_id": user_resp["id"]})