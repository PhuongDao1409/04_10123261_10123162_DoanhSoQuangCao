import os
import time
import uuid
import logging
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("backend")

app = FastAPI(title="Advertising Backend Gateway - 4 Models", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.state.req_id = req_id
    start_time = time.time()
    logger.info(f"backend | req={req_id} | {request.method} {request.url.path} -> Bắt đầu")
    response = await call_next(request)
    process_time = int((time.time() - start_time) * 1000)
    logger.info(f"backend | req={req_id} | Status: {response.status_code} | Thời gian: {process_time}ms")
    return response

class PredictInput(BaseModel):
    TV: float = Field(..., ge=0)
    Radio: float = Field(..., ge=0)
    Newspaper: float = Field(..., ge=0)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "backend"}

@app.post("/api/predict/{model_name}")
def predict_proxy(model_name: str, data: PredictInput, request: Request):
    req_id = getattr(request.state, "req_id", "internal")
    try:
        res = requests.post(f"{AI_SERVICE_URL}/predict/{model_name}", json=data.dict(), timeout=5)
        return res.json()
    except Exception as e:
        logger.error(f"backend | req={req_id} | Lỗi: {str(e)}")
        raise HTTPException(status_code=502, detail="Lỗi kết nối AI Service")
