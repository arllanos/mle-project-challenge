import json
import logging
import time
import uuid
from datetime import datetime, timezone

import mlflow
import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from common.config import HousingPredictorConfig as config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = config.OUTPUT_DIR
DEMOGRAPHICS_PATH = config.DEMOGRAPHICS_PATH
MODEL_FEATURES_PATH = config.MODEL_FEATURES_PATH
MLFLOW_TRACKING_URI = config.MLFLOW_TRACKING_URI
MODEL_URI = config.MODEL_URI

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

try:
    # Loading the model from the local MLflow artifact store
    model = mlflow.pyfunc.load_model(config.MODEL_URI)
    demographics = pd.read_csv(DEMOGRAPHICS_PATH)
    with open(MODEL_FEATURES_PATH, "r") as f:
        model_features = json.load(f)
except Exception as e:
    logger.error(f"Failed to load model or data: {e}")
    raise RuntimeError("Model or data could not be loaded.") from e

app = FastAPI()


class BasicProperty(BaseModel):
    bedrooms: float = Field(..., example=4, description="Number of bedrooms.")
    bathrooms: float = Field(..., example=1.0, description="Number of bathrooms.")
    sqft_living: int = Field(..., example=1680, description="Living area in square feet.")
    sqft_lot: int = Field(..., example=5043, description="Lot size in square feet.")
    floors: float = Field(..., example=1.5, description="Number of floors.")
    sqft_above: int = Field(..., example=1680, description="Square footage above ground.")
    sqft_basement: int = Field(..., example=0, description="Basement area in square feet.")
    view: int = Field(..., example=0, description="Quality of view (0-4 scale).")
    grade: int = Field(..., example=6, description="Construction grade (1-13 scale).")
    sqft_living15: int = Field(..., example=1560, description="Avg living area of 15 nearest neighbors.")
    zipcode: int = Field(..., example=98118, description="ZIP code of the property.")


class Property(BasicProperty):
    waterfront: int = Field(..., example=0, description="Waterfront presence (1=yes, 0=no).")
    condition: int = Field(..., example=4, description="Condition (1-5 scale).")
    yr_built: int = Field(..., example=1911, description="Year built.")
    yr_renovated: int = Field(..., example=0, description="Year renovated.")
    lat: float = Field(..., example=47.5354, description="Latitude.")
    long: float = Field(..., example=-122.273, description="Longitude.")
    sqft_lot15: int = Field(..., example=5765, description="Avg lot size of 15 nearest neighbors.")


def process_property(property, model, demographics, model_features):
    start_time = time.time()
    property_df = pd.DataFrame([property.model_dump()])
    property_df = property_df.merge(demographics, how="left", on="zipcode")
    property_df = property_df[model_features]  # TODO are there any missing values in model_features?

    prediction = model.predict(property_df)
    end_time = time.time()

    request_id = str(uuid.uuid4())

    return {
        "prediction": prediction[0],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "processing_time_ms": (end_time - start_time) * 1000,
        "input_features": property.dict(),
    }


@app.post("/predict/")
async def predict(property: Property):
    return process_property(property, model, demographics, model_features)


@app.post("/predict-basic/")
async def predict_basic(property: BasicProperty):
    return process_property(property, model, demographics, model_features)
