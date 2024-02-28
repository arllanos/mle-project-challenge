import logging

from starlette.config import Config

logger = logging.getLogger(__name__)


class HousingPredictorConfig:
    config = Config()
    APP_NAME = config("APP_NAME", default="housing-price-predictor")

    # paths
    SALES_PATH = config("SALES_PATH", default="data/kc_house_data.csv")
    DEMOGRAPHICS_PATH = config("DEMOGRAPHICS_PATH", default="data/zipcode_demographics.csv")
    OUTPUT_DIR = config("OUTPUT_DIR", default="model")
    MODEL_FEATURES_PATH = f"{OUTPUT_DIR}/model_features.json"

    # mlflow
    MLFLOW_TRACKING_URI = config("MLFLOW_TRACKING_URI", default="http://localhost:5001")

    # model
    MODEL_NAME = config("MODEL_NAME", default="housing-price-reg-model")
    MODEL_VERSION = config("MODEL_VERSION", default="1")
    MODEL_URI = f"models:/{MODEL_NAME}/{MODEL_VERSION}"
