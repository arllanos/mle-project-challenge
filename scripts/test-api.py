import requests
import pandas as pd

URL = "http://localhost:8000/predict/"
EXAMPLES_PATH = "data/future_unseen_examples.csv"

examples_df = pd.read_csv(EXAMPLES_PATH)
examples = examples_df.to_dict(orient="records")

def send_request(example):
    response = requests.post(URL, json=example)
    return response.json()

if __name__ == "__main__":
    for example in examples:
        response = send_request(example)
        print(f"Request: {example}\nResponse: {response}\n")
