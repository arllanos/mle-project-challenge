# MLE Project Challenge
![CI Status](https://github.com/arllanos/mle-project-challenge/actions/workflows/ci-main.yml/badge.svg)

This document provides notes for the MLE Project Challenge, detailing the setup and usage instructions for the Housing Price Predictor API.

## Key Components
![alt text](image.png)

## Setup

Ensure you have Anaconda (or Miniconda) installed to manage environments and dependencies.

### 1. Get the Code
Get the code clonning the repo:
```sh
git clone git@github.com:arllanos/mle-project-challenge.git
```

### 2. Create and Activate the Conda Environment
Use the following commands to create and activate the conda environment:

```sh
# create the environment from the YAML file
conda env update -f conda_environment.yml

# activate the newly created environment
conda activate housing
```
After activation, verify that the correct Python interpreter from the Conda environment is being used:
```sh
which python
```
If the output doesn't point to the Anaconda directory's Python interpreter, adjust your `PATH`.
```sh
# fix your path
export PATH="$HOME/miniconda3/envs/housing/bin:$PATH"

# retry activating the newly created environment
conda activate housing
```

### 3. Python Package Installation
```sh
pip3 install -U pip wheel "setuptools<60"
pip3 install -e ".[dev]"
```

## Start the MLFlow Tracking Server

In this exercise, we leverage MLflow's Model Registry to enable experiment tracking and model versioning. This process involves setting up an MLflow tracking server. The MLflow client can interface with various backend and artifact storage configurations. In our case, we configure the MLflow server to run on localhost with SQLite as the backend and artifact storage in local file system.

```sh
mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root $(PWD)/mlruns --host 0.0.0.0 --port 5001
```

Now, you can visualize experiments and models by navigating to http://127.0.0.1:5001/

## Create the model

To train the housing price prediction model, execute the `create_model.py` script. This process will generate and store the model artifacts in the `model` directory. Additionally, the script is configured to log the model artifacts to the MLflow Model Registry for versioning and tracking.

```sh
python create_model.py
```

## Run the Housing Price Predictor API

You can run the API locally, using Docker, or using a Docker image from GHCR. Choose the method that best suits your needs.

### Option 1: Run Locally From Your Terminal
```sh
uvicorn api.app:app --reload
```
 
### Option 2: Run Using Docker - Building Image Locally
```sh
docker build -t housing-price-predictor-api .

docker run --name housing --rm \
-v $(pwd)/model/:/usr/src/app/model/ \
-v $(pwd)/mlruns:$(pwd)/mlruns/ \
-e MLFLOW_TRACKING_URI=http://host.docker.internal:5001 \
-p 8000:8000 \
housing-price-predictor-api
```

### Option 3: Run using Docker - Pulling Remote Image built by CI
```sh
# latest tag
docker run --name housing --rm \
-v $(pwd)/model/:/usr/src/app/model/ \
-v $(pwd)/mlruns:$(pwd)/mlruns/ \
-e MLFLOW_TRACKING_URI=http://host.docker.internal:5001 \
-p 8000:8000 \
ghcr.io/arllanos/mle-project-challenge/housing-price-predictor-api:latest

# with specific commit SHA tag
COMMIT_SHA=<commit_sha>

docker run --name housing --rm \
-v $(pwd)/model/:/usr/src/app/model/ \
-v $(pwd)/mlruns:$(pwd)/mlruns/ \
-e MLFLOW_TRACKING_URI=http://host.docker.internal:5001 \
-p 8000:8000 \
ghcr.io/arllanos/mle-project-challenge/housing-price-predictor-api:${COMMIT_SHA}
```

## Request Predictions
### Option 1: Using Test Script
```sh
python scripts/predict_examples.py
```

### Option 2: Using Swagger
Navigate to http://127.0.0.1:8000/docs and execute the `predict` or `predict-basic` endpoints.
