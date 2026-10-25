"""FastAPI routes for the credit-card assignment app."""

import json
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.features import CLASSIFICATION_FEATURES, REGRESSION_FEATURES

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"
STATIC_DIR = ROOT / "app" / "static"

app = FastAPI(
    title="Credit Default ML Lab",
    description="A student-friendly demo of regression and classification.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class RegressionInput(BaseModel):
    sex: int = Field(ge=1, le=2)
    education: int = Field(ge=1, le=6)
    marriage: int = Field(ge=1, le=3)
    age: int = Field(ge=18, le=120)
    pay_0: int = Field(ge=-2, le=8)
    pay_2: int = Field(ge=-2, le=8)
    bill_amt1: float = Field(allow_inf_nan=False)
    pay_amt1: float = Field(allow_inf_nan=False)


class ClassificationInput(RegressionInput):
    limit_bal: float = Field(ge=0, allow_inf_nan=False)


@lru_cache(maxsize=2)
def load_pipeline(filename: str):
    path = MODEL_DIR / filename
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail="Models are not trained yet. Run: python train_models.py",
        )
    return joblib.load(path)


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/metrics")
def get_metrics() -> dict:
    path = MODEL_DIR / "metrics.json"
    if not path.exists():
        raise HTTPException(status_code=503, detail="Train the models to create metrics.")
    return json.loads(path.read_text())


@app.post("/predict/regression")
def predict_regression(payload: RegressionInput) -> dict:
    model = load_pipeline("regression_pipeline.joblib")
    row = pd.DataFrame(
        [[getattr(payload, field.lower()) for field in REGRESSION_FEATURES]],
        columns=REGRESSION_FEATURES,
    )
    prediction = float(model.predict(row)[0])
    return {"prediction": round(max(0.0, prediction), 2), "unit": "NT dollars"}


@app.post("/predict/classification")
def predict_classification(payload: ClassificationInput) -> dict:
    model = load_pipeline("classification_pipeline.joblib")
    values = payload.model_dump()
    row = pd.DataFrame(
        [[values[field.lower()] for field in CLASSIFICATION_FEATURES]],
        columns=CLASSIFICATION_FEATURES,
    )
    prediction = int(model.predict(row)[0])
    return {
        "prediction": prediction,
        "label": "Likely to default" if prediction == 1 else "Not predicted to default",
    }
