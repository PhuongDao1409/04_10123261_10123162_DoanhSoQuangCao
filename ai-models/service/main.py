import os
import json
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Advertising Sales AI Service", version="1.0.0")

# Biến toàn cục lưu trữ Model & Metadata
MODEL_PATH = "models/model.joblib"
METADATA_PATH = "models/metadata.json"
SCHEMA_PATH = "models/schema.json"

model = None
metadata = {}
schema = {}

@app.on_event("startup")
def load_artifacts():
    global model, metadata, schema
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"[AI-SERVICE] Đã nạp thành công model từ {MODEL_PATH}")
    else:
        print(f"[AI-SERVICE] CẢNH BÁO: Không tìm thấy {MODEL_PATH}")

    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)

class PredictRequest(BaseModel):
    TV: float = Field(..., example=230.1)
    Radio: float = Field(..., example=37.8)
    Newspaper: float = Field(..., example=69.2)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ai-service",
        "model_loaded": model is not None,
        "model_name": metadata.get("model_name", "Unknown")
    }

@app.get("/model-info")
def model_info():
    return {
        "metadata": metadata,
        "schema": schema
    }

@app.post("/predict")
def predict(data: PredictRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Mô hình chưa được nạp!")
    
    input_df = pd.DataFrame([{
        "TV": data.TV,
        "Radio": data.Radio,
        "Newspaper": data.Newspaper
    }])
    
    prediction = float(model.predict(input_df)[0])
    
    return {
        "prediction": round(prediction, 2),
        "unit": "nghìn sản phẩm",
        "model_version": metadata.get("model_version", "1.0.0"),
        "model_name": metadata.get("model_name", "Best Model")
    }
