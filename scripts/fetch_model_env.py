import mlflow

from common.config import HousingPredictorConfig as config

MLFLOW_TRACKING_URI = config.MLFLOW_TRACKING_URI
MODEL_URI = config.MODEL_URI


mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


env_path = mlflow.pyfunc.get_model_dependencies(MODEL_URI)

print(env_path)
