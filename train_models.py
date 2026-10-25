"""Train and save the assignment's regression and classification models."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.features import (
    CLASSIFICATION_FEATURES,
    CLASSIFICATION_TARGET,
    REGRESSION_FEATURES,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT / "data" / "default of credit card clients.xls"
DEFAULT_MODELS = ROOT / "models"


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}. Download or place it there first.")

    if path.suffix.lower() in {".xls", ".xlsx"}:
        frame = pd.read_excel(path, header=1)
    else:
        frame = pd.read_csv(path)

    frame.columns = [
        str(column).strip().replace(" ", "_").replace(".", "_")
        for column in frame.columns
    ]
    return frame


def train_and_save(data_path: Path = DEFAULT_DATA, models_dir: Path = DEFAULT_MODELS) -> dict:
    data = load_dataset(data_path)
    needed = set(REGRESSION_FEATURES + CLASSIFICATION_FEATURES + ["LIMIT_BAL", CLASSIFICATION_TARGET])
    missing = sorted(needed.difference(data.columns))
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {', '.join(missing)}")

    x_reg = data[REGRESSION_FEATURES]
    y_reg = data["LIMIT_BAL"]
    x_reg_train, x_reg_test, y_reg_train, y_reg_test = train_test_split(
        x_reg, y_reg, test_size=0.2, random_state=42
    )
    regression_model = make_pipeline(StandardScaler(), LinearRegression())
    regression_model.fit(x_reg_train, y_reg_train)
    regression_r2 = r2_score(y_reg_test, regression_model.predict(x_reg_test))

    x_class = data[CLASSIFICATION_FEATURES]
    y_class = data[CLASSIFICATION_TARGET].astype(int)
    x_class_train, x_class_test, y_class_train, y_class_test = train_test_split(
        x_class,
        y_class,
        test_size=0.2,
        random_state=42,
        stratify=y_class,
    )
    classification_model = make_pipeline(
        StandardScaler(),
        LogisticRegression(solver="liblinear", max_iter=1000),
    )
    classification_model.fit(x_class_train, y_class_train)
    class_accuracy = accuracy_score(y_class_test, classification_model.predict(x_class_test))

    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(regression_model, models_dir / "regression_pipeline.joblib")
    joblib.dump(classification_model, models_dir / "classification_pipeline.joblib")

    metrics = {
        "dataset_rows": int(len(data)),
        "test_rows": int(len(y_reg_test)),
        "regression_target": "LIMIT_BAL (credit limit in NT dollars)",
        "regression_r2": round(float(regression_r2), 4),
        "classification_target": "default_payment_next_month (0 or 1)",
        "classification_accuracy": round(float(class_accuracy), 4),
        "classification_test_rows": int(len(y_class_test)),
    }
    (models_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")

    print(f"Regression R² (test set): {metrics['regression_r2']}")
    print(f"Classification accuracy (test set): {metrics['classification_accuracy']}")
    print(f"Saved model files and metrics to: {models_dir}")
    return metrics


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Excel or CSV dataset path")
    parser.add_argument("--models-dir", type=Path, default=DEFAULT_MODELS)
    args = parser.parse_args()
    train_and_save(args.data, args.models_dir)


if __name__ == "__main__":
    main()
