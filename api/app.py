import json
import logging
import pickle
import time
import uuid
from datetime import datetime, timezone

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = "model"
DEMOGRAPHICS_PATH = "data/zipcode_demographics.csv"
MODEL_PATH = f"{MODEL_DIR}/model.pkl"
MODEL_FEATURES_PATH = f"{MODEL_DIR}/model_features.json"
MODEL_VERSION = "1.0.0"   # TODO: update according to the versioning system implemented

# loading data and model outside of request handler
try:
    model = pickle.load(open(MODEL_PATH, "rb"))
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
    zipcode: int = Field(..., example=98118, description="ZIP code of the property.")


class Property(BasicProperty):
    waterfront: int = Field(..., example=0, description="Waterfront presence (1=yes, 0=no).")
    view: int = Field(..., example=0, description="Quality of view (0-4 scale).")
    condition: int = Field(..., example=4, description="Condition (1-5 scale).")
    grade: int = Field(..., example=6, description="Construction grade (1-13 scale).")
    yr_built: int = Field(..., example=1911, description="Year built.")
    yr_renovated: int = Field(..., example=0, description="Year renovated.")
    lat: float = Field(..., example=47.5354, description="Latitude.")
    long: float = Field(..., example=-122.273, description="Longitude.")
    sqft_living15: int = Field(..., example=1560, description="Avg living area of 15 nearest neighbors.")
    sqft_lot15: int = Field(..., example=5765, description="Avg lot size of 15 nearest neighbors.")


def process_property(property, model, demographics, model_features, model_version):
    start_time = time.time()
    property_df = pd.DataFrame([property.model_dump()])
    property_df = property_df.merge(demographics, how="left", on="zipcode")
    property_df = property_df[model_features]  # TODO are there any missing values in model_features?

    prediction = model.predict(property_df)
    end_time = time.time()

    request_id = str(uuid.uuid4())

    return {
        "prediction": prediction[0],
        "model_version": model_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "processing_time_ms": (end_time - start_time) * 1000,
        "input_features": property.dict(),
    }


@app.post("/predict/")
async def predict(property: Property):
    return process_property(property, model, demographics, model_features, MODEL_VERSION)


@app.post("/predict-basic/")
async def predict_basic(property: BasicProperty):
    return process_property(property, model, demographics, model_features, MODEL_VERSION)
