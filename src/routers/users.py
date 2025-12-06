from fastapi import APIRouter, Depends
from src.nats_client import nats_client
from src.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def get_my_profile(user: dict = Depends(get_current_user)):
    
    payload = {"keycloak_id": user["keycloak_id"]}
    
    response = await nats_client.request("users.get", payload)
    
    if "error" in response and response["error"] == "User not found":
        sync_payload = {
            "keycloak_id": user["keycloak_id"],
            "username": user["username"]
        }
        response = await nats_client.request("users.create", sync_payload)
        
    return response

@router.put("/me")
async def update_my_profile(data: dict, user: dict = Depends(get_current_user)):
    payload = {
        "keycloak_id": user["keycloak_id"],
        "username": data.get("username")
    }
    return await nats_client.request("users.update", payload)