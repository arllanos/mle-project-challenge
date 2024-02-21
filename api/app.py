from fastapi import FastAPI
from pydantic import BaseModel, Field
import pickle
import pandas as pd
import json

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = "model"
DEMOGRAPHICS_PATH = 'data/zipcode_demographics.csv'
MODEL_PATH = f"{MODEL_DIR}/model.pkl"
MODEL_FEATURES_PATH = f"{MODEL_DIR}/model_features.json"

# loading data and model outside of request handler
try:
    model = pickle.load(open(MODEL_PATH, "rb"))
    demographics = pd.read_csv(DEMOGRAPHICS_PATH)
    with open(MODEL_FEATURES_PATH, "r") as f:
        model_features = json.load(f)
except Exception as e:
    logger.error(f"Failed to load model or data: {e}")
    raise RuntimeError("Model or data could not be loaded.")

app = FastAPI()

class Property(BaseModel):
    bedrooms: float = Field(..., example=4)
    bathrooms: float = Field(..., example=1.0)
    sqft_living: int = Field(..., example=1680)
    sqft_lot: int = Field(..., example=5043)
    floors: float = Field(..., example=1.5)
    waterfront: int = Field(..., example=0)
    view: int = Field(..., example=0)
    condition: int = Field(..., example=4)
    grade: int = Field(..., example=6)
    sqft_above: int = Field(..., example=1680)
    sqft_basement: int = Field(..., example=0)
    yr_built: int = Field(..., example=1911)
    yr_renovated: int = Field(..., example=0)
    zipcode: int = Field(..., example=98118)
    lat: float = Field(..., example=47.5354)
    long: float = Field(..., example=-122.273)
    sqft_living15: int = Field(..., example=1560)
    sqft_lot15: int = Field(..., example=5765)


@app.post("/predict/")
async def predict(property: Property):
    # property_df = pd.DataFrame([property.dict()])
    property_df = pd.DataFrame([property.model_dump()])

    # merge with demographic data
    property_df = property_df.merge(demographics, how="left", on="zipcode")
    
    # select columns according to the model's training
    property_df = property_df[model_features]

    prediction = model.predict(property_df)

    return {"prediction": prediction[0]}
