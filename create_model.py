import json
import pathlib
import pickle
from typing import List, Tuple

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn import model_selection, neighbors, pipeline, preprocessing
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from common.config import HousingPredictorConfig as config

SALES_PATH = config.SALES_PATH
DEMOGRAPHICS_PATH = config.DEMOGRAPHICS_PATH
# List of columns (subset) that will be taken from home sale data
SALES_COLUMN_SELECTION = [
    'price', 'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors',
    'sqft_above', 'sqft_basement', 'zipcode',
    'grade', 'sqft_living15', 'view'
]
OUTPUT_DIR = config.OUTPUT_DIR
MLFLOW_TRACKING_URI = config.MLFLOW_TRACKING_URI

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


def load_data(
    sales_path: str,
    demographics_path: str,
    sales_column_selection: List[str],
    demographics_column_selection: List[str] = None,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Load the target and feature data by merging sales and demographics.

    Args:
        sales_path: path to CSV file with home sale data
        demographics_path: path to CSV file with home sale data
        sales_column_selection: list of columns from sales data to be used as
            features

    Returns:
        Tuple containg with two elements: a DataFrame and a Series of the same
        length.  The DataFrame contains features for machine learning, the
        series contains the target variable (home sale price).

    """
    data = pd.read_csv(sales_path, usecols=sales_column_selection, dtype={"zipcode": str})

    # Load demographics data, handle None by omitting usecols parameter
    if demographics_column_selection is None:
        demographics = pd.read_csv(demographics_path, dtype={"zipcode": str})
    else:
        demographics = pd.read_csv(
            demographics_path, usecols=demographics_column_selection, dtype={"zipcode": str}
        )

    merged_data = data.merge(demographics, how="left", on="zipcode").drop(columns="zipcode")
    # Remove the target variable from the dataframe, features will remain
    y = merged_data.pop("price")
    x = merged_data

    return x, y


def evaluate_model(_y_test, y_pred):
    mae = mean_absolute_error(_y_test, y_pred)
    mse = mean_squared_error(_y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(_y_test, y_pred)

    return mae, mse, rmse, r2


def main():
    """Load data, train model, and export artifacts."""

    mlflow.set_experiment("Housing Price Prediction")

    with mlflow.start_run() as run:
        x, y = load_data(SALES_PATH, DEMOGRAPHICS_PATH, SALES_COLUMN_SELECTION)
        x_train, _x_test, y_train, _y_test = model_selection.train_test_split(
            x, y, test_size=0.2, random_state=42
        )

        model = pipeline.make_pipeline(preprocessing.RobustScaler(), neighbors.KNeighborsRegressor()).fit(
            x_train, y_train
        )

        y_pred = model.predict(_x_test)

        mae, mse, rmse, r2 = evaluate_model(_y_test, y_pred)

        mlflow.log_metrics({"mae": mae, "mse": mse, "rmse": rmse, "r2": r2})

        output_dir = pathlib.Path(OUTPUT_DIR)
        output_dir.mkdir(exist_ok=True)
        features_path = output_dir / "model_features.json"

        # Output model artifacts: pickled model and JSON list of features
        pickle.dump(model, open(output_dir / "model.pkl", "wb"))
        with open(features_path, "w") as f:
            json.dump(list(x_train.columns), f)

        # Output model artifacts to MLflow
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="housing-price-model",
            registered_model_name="housing-price-reg-model",
        )
        mlflow.log_artifact(str(features_path), "model_features.json")

        print(f"Mlflow Run Name: {run.info.run_name}\n")


if __name__ == "__main__":
    main()
