import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Advertising AI Service - 4 Models", version="2.0.0")

models = {}
MODEL_NAMES = ["linear", "ridge", "random_forest", "xgboost"]

@app.on_event("startup")
def load_all_models():
    for name in MODEL_NAMES:
        path = f"models/{name}.joblib"
        if os.path.exists(path):
            models[name] = joblib.load(path)
            print(f"[AI-SERVICE] Đã nạp thành công: {path}")
        else:
            print(f"[AI-SERVICE] CẢNH BÁO: Thiếu file {path}")

class PredictRequest(BaseModel):
    TV: float = Field(..., example=150.0)
    Radio: float = Field(..., example=25.0)
    Newspaper: float = Field(..., example=20.0)

@app.get("/health")
def health():
    return {"status": "healthy", "loaded_models": list(models.keys())}

@app.post("/predict/{model_name}")
def predict(model_name: str, data: PredictRequest):
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' không tồn tại. Chọn trong: {MODEL_NAMES}")
    
    model = models[model_name]
    input_df = pd.DataFrame([data.dict()])
    prediction = float(model.predict(input_df)[0])
    
    return {
        "model": model_name,
        "prediction": round(prediction, 2),
        "unit": "nghìn sản phẩm"
    }
