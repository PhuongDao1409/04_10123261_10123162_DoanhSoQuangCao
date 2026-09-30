import os
import time
import uuid
import logging
import requests
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("backend")

app = FastAPI(title="Advertising Backend Gateway - 4 Models", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")

import certifi

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client["advertising_db"]
    history_collection = db["prediction_history"]
    client.server_info()
    logger.info("Kết nối MongoDB thành công!")
except Exception as e:
    logger.warning(f"Không thể kết nối MongoDB: {str(e)}")
    history_collection = None

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
    db_status = "connected" if history_collection is not None else "disconnected"
    return {"status": "healthy", "service": "backend", "mongodb": db_status}

@app.get("/api/history")
def get_history(limit: int = 10):
    if history_collection is None:
        return {"history": []}
    docs = list(history_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
    return {"history": docs}

@app.post("/api/predict/{model_name}")
def predict_proxy(model_name: str, data: PredictInput, request: Request):
    req_id = getattr(request.state, "req_id", "internal")
    try:
        url = f"{AI_SERVICE_URL}/predict/{model_name}"
        logger.info(f"backend | req={req_id} | Đang gọi AI Service tại: {url}")
        
        res = requests.post(url, json=data.dict(), timeout=5)
        
        if res.status_code != 200:
            logger.error(f"backend | req={req_id} | AI Service trả về lỗi {res.status_code}: {res.text}")
            raise HTTPException(status_code=res.status_code, detail=res.text)
        
        result = res.json()
        result["request_id"] = req_id
        
        if history_collection is not None:
            record = {
                "request_id": req_id,
                "model": model_name,
                "input": data.dict(),
                "prediction": result["prediction"],
                "unit": result["unit"],
                "timestamp": datetime.utcnow()
            }
            history_collection.insert_one(record)
            
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"backend | req={req_id} | Không thể kết nối AI Service: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Không thể kết nối đến AI Service: {str(e)}")
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"backend | req={req_id} | Lỗi không xác định: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
