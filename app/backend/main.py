import os
import time
import uuid
import logging
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Cấu hình Logging đúng chuẩn thầy yêu cầu (in ra terminal thời gian thực)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("backend")

app = FastAPI(title="Advertising Backend Gateway", version="1.0.0")

# Bật CORS cho phép Frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")

# Middleware tự động gắn request_id và tính độ trễ xử lý
@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.state.req_id = req_id
    start_time = time.time()
    
    logger.info(f"backend | req={req_id} | {request.method} {request.url.path} -> Bắt đầu xử lý")
    
    response = await call_next(request)
    
    process_time = int((time.time() - start_time) * 1000)
    response.headers["X-Request-ID"] = req_id
    logger.info(f"backend | req={req_id} | Status: {response.status_code} | Tổng thời gian: {process_time}ms")
    return response

class PredictInput(BaseModel):
    TV: float = Field(..., ge=0, example=230.1)
    Radio: float = Field(..., ge=0, example=37.8)
    Newspaper: float = Field(..., ge=0, example=69.2)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "backend",
        "ai_service_target": AI_SERVICE_URL
    }

@app.get("/api/model-info")
def get_model_info(request: Request):
    req_id = getattr(request.state, "req_id", "internal")
    try:
        res = requests.get(f"{AI_SERVICE_URL}/model-info", timeout=5)
        return res.json()
    except Exception as e:
        logger.error(f"backend | req={req_id} | Lỗi khi gọi AI Service: {str(e)}")
        raise HTTPException(status_code=502, detail="Không kết nối được tới AI Service")

@app.post("/api/predict")
def predict_sales(data: PredictInput, request: Request):
    req_id = getattr(request.state, "req_id", "internal")
    logger.info(f"backend | req={req_id} | Validate đầu vào thành công: {data.dict()} -> Chuyển sang AI Service")
    
    try:
        res = requests.post(f"{AI_SERVICE_URL}/predict", json=data.dict(), timeout=5)
        if res.status_code != 200:
            logger.error(f"backend | req={req_id} | AI Service trả mã lỗi: {res.status_code}")
            raise HTTPException(status_code=res.status_code, detail=res.text)
        
        result = res.json()
        result["request_id"] = req_id
        logger.info(f"backend | req={req_id} | Nhận kết quả từ AI Service: {result['prediction']} {result['unit']}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"backend | req={req_id} | Không thể kết nối AI Service: {str(e)}")
        raise HTTPException(status_code=503, detail="AI Service hiện không phản hồi")
