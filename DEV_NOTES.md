# MLE Project Challenge
![CI Status](https://github.com/arllanos/mle-project-challenge/actions/workflows/ci-main.yml/badge.svg)

This document provides development notes for the MLE Project Challenge, detailing the setup and usage instructions for the Housing Price Predictor API.

## Setup

Ensure you have Anaconda installed to manage environments and dependencies.

Use the following commands to create and activate the conda environment:

```sh
conda env create -f conda_environment.yml
conda activate housing 
```

### Create the model

Run `create_model.py` to train the housing price prediction model. This script generates model artifacts in the `model` directory.

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

docker run --name housing --rm -v $(pwd)/model/:/usr/src/app/model/ -p 8000:8000 housing-price-predictor-api
```

### Option 3: Run using Docker - Pulling Remote Image
```sh
# latest tag
docker run --name housing --rm -v $(pwd)/model/:/usr/src/app/model/ -p 8000:8000 ghcr.io/arllanos/mle-project-challenge/housing-price-predictor-api:latest

# with specific commit SHA tag
COMMIT_SHA=<commit_sha>

docker run --name housing --rm -v $(pwd)/model/:/usr/src/app/model/ -p 8000:8000 ghcr.io/arllanos/mle-project-challenge/housing-price-predictor-api:${COMMIT_SHA}
```

## Request Predictions
### Option 1: Using Test Script
```sh
python scripts/test-api.py
```

### Option 2: Using Swagger
Navigate to http://localhost:8000/docs and exeucte the `predict` or `predict-basic` endpoints.
