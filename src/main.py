from fastapi import FastAPI
import logfire

from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator

from src.config import settings
from src.nats_client import nats_client
from src.routers import users, exercises, attempts, ai, code_execution


logfire.configure()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting API Gateway...")
    await nats_client.connect()
    yield
    print("Shutting down API Gateway...")
    await nats_client.close()

app = FastAPI(title="CodeSnap API Gateway", lifespan=lifespan)
logfire.instrument_fastapi(app)

origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(attempts.router)
app.include_router(ai.router)
app.include_router(code_execution.router)

@app.get("/health")
async def health():
    return {"status": "gateway-active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.port)