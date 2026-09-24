import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)

def test_backend_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_predict_validation_error():
    # Test nhap gia tri am phai bao loi 422
    res = client.post("/api/predict", json={"TV": -10, "Radio": 20, "Newspaper": 10})
    assert res.status_code == 422

def test_predict_missing_fields():
    # Test thieu truong du lieu phai bao loi 422
    res = client.post("/api/predict", json={"TV": 100})
    assert res.status_code == 422

def test_predict_edge_cases():
    # Test gia tri 0 van hop le
    res = client.post("/api/predict", json={"TV": 0, "Radio": 0, "Newspaper": 0})
    assert res.status_code in [200, 502, 503]
