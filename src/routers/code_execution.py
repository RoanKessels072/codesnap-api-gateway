from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.nats_client import nats_client
from src.auth import get_current_user

router = APIRouter(prefix="/code", tags=["Code Execution"])

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    mode: Optional[str] = "run"

@router.post("/execute")
async def execute_code_route(
    request_data: CodeExecutionRequest, 
    user: dict = Depends(get_current_user)
):
    payload = {
        "code": request_data.code,
        "language": request_data.language,
        "mode": request_data.mode 
    }

    try:
        response = await nats_client.request("execution.run", payload, timeout=10)
        if response and response.get("error"):
            if response.get("error") == "Execution timed out":
                raise HTTPException(status_code=408, detail="Execution timed out")
            
            raise HTTPException(status_code=400, detail=response["error"])
            
        return response

    except TimeoutError:
        raise HTTPException(status_code=504, detail="Service unavailable (NATS Timeout)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))