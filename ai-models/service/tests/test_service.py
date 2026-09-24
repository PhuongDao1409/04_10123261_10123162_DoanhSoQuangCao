import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)

def test_ai_health():
    res = client.get("/health")
    assert res.status_code == 200

def test_ai_model_info():
    res = client.get("/model-info")
    assert res.status_code == 200

def test_ai_predict_format():
    res = client.post("/predict", json={"TV": 150.0, "Radio": 25.0, "Newspaper": 20.0})
    if res.status_code == 200:
        data = res.json()
        assert "prediction" in data
        assert "unit" in data
