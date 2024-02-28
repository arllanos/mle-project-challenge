import pytest
from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


# Happy path tests
@pytest.mark.parametrize(
    "property_data, expected_status_code",
    [
        (
            {
                "bedrooms": 3,
                "bathrooms": 2,
                "sqft_living": 2000,
                "sqft_lot": 5000,
                "floors": 2,
                "sqft_above": 1500,
                "sqft_basement": 500,
                "zipcode": 98118,
                "waterfront": 0,
                "view": 3,
                "condition": 5,
                "grade": 7,
                "yr_built": 1980,
                "yr_renovated": 0,
                "lat": 47.5112,
                "long": -122.257,
                "sqft_living15": 1890,
                "sqft_lot15": 4750,
            },
            200,
        ),
        (
            {
                "bedrooms": 2,
                "bathrooms": 1,
                "sqft_living": 1200,
                "sqft_lot": 6000,
                "floors": 1,
                "sqft_above": 1200,
                "sqft_basement": 0,
                "zipcode": 98028,
                "waterfront": 1,
                "view": 4,
                "condition": 3,
                "grade": 9,
                "yr_built": 1960,
                "yr_renovated": 2005,
                "lat": 47.7379,
                "long": -122.233,
                "sqft_living15": 2020,
                "sqft_lot15": 7460,
            },
            200,
        ),
    ],
    ids=["typical-house", "waterfront-house"],
)
def test_predict_endpoint_happy_path(property_data, expected_status_code):
    # Act
    response = client.post("/predict/", json=property_data)

    # Assert
    assert response.status_code == expected_status_code
    assert "prediction" in response.json()


# Error cases
@pytest.mark.parametrize(
    "property_data, expected_status_code",
    [
        (
            {
                "bedrooms": "three",
                "bathrooms": 2,
                "sqft_living": 2000,
                "sqft_lot": 5000,
                "floors": 2,
                "sqft_above": 1500,
                "sqft_basement": 500,
                "zipcode": 98118,
                "waterfront": 0,
                "view": 3,
                "condition": 5,
                "grade": 7,
                "yr_built": 1980,
                "yr_renovated": 0,
                "lat": 47.5112,
                "long": -122.257,
                "sqft_living15": 1890,
                "sqft_lot15": 4750,
            },
            422,
        ),
        (
            {
                "sqft_living": 2000,
                "sqft_lot": 5000,
                "floors": 2,
                "sqft_above": 1500,
                "sqft_basement": 500,
                "zipcode": 98118,
            },
            422,
        ),
    ],
    ids=["invalid-bedrooms-type", "missing-required-fields"],
)
def test_predict_endpoint_error_cases(property_data, expected_status_code):
    # Act
    response = client.post("/predict/", json=property_data)

    # Assert
    assert response.status_code == expected_status_code
    assert "detail" in response.json()
