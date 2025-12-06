from fastapi import APIRouter, Depends, HTTPException
from src.nats_client import nats_client
from src.auth import get_current_user

router = APIRouter(prefix="/exercises", tags=["Exercises"])

@router.get("/")
async def list_exercises(user: dict = Depends(get_current_user)):
    return await nats_client.request("exercises.list", {})

@router.get("/{exercise_id}")
async def get_exercise(exercise_id: int, user: dict = Depends(get_current_user)):
    response = await nats_client.request("exercises.get", {"id": exercise_id})
    if not response or "error" in response:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return response

#Don't have an admin role yet, so this is not accessible
@router.post("/")
async def create_exercise(data: dict, user: dict = Depends(get_current_user)):
    if "admin" not in user["roles"]:
       raise HTTPException(status_code=403, detail="Admins only")
       
    return await nats_client.request("exercises.create", data)