import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Advertising AI Service - 4 Models", version="3.0.0")

models = {}
MODEL_NAMES = ["linear", "ridge", "random_forest", "xgboost"]

@app.on_event("startup")
def load_all_models():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for name in MODEL_NAMES:
        possible_paths = [
            os.path.join(current_dir, f"models/{name}.joblib"),
            os.path.join(current_dir, f"../models/{name}.joblib"),
            f"/app/models/{name}.joblib",
            f"models/{name}.joblib",
            f"ai-models/models/{name}.joblib"
        ]
        loaded = False
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    models[name] = joblib.load(path)
                    print(f"[AI-SERVICE] Đã nạp thành công '{name}' từ: {path}")
                    loaded = True
                    break
                except Exception as e:
                    print(f"[AI-SERVICE] Lỗi khi load file {path}: {str(e)}")
        if not loaded:
            print(f"[AI-SERVICE] CẢNH BÁO: Không tìm thấy file model cho '{name}'!")

class PredictRequest(BaseModel):
    TV: float = Field(..., example=150.0)
    Radio: float = Field(..., example=25.0)
    Newspaper: float = Field(..., ge=0, example=20.0)

@app.get("/health")
def health():
    return {"status": "healthy", "loaded_models": list(models.keys())}

@app.post("/predict/{model_name}")
def predict(model_name: str, data: PredictRequest):
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' không tồn tại. Có sẵn: {list(models.keys())}")
    
    model = models[model_name]
    input_df = pd.DataFrame([data.dict()])
    prediction = float(model.predict(input_df)[0])
    
    return {
        "model": model_name,
        "prediction": round(prediction, 2),
        "unit": "nghìn sản phẩm"
    }
