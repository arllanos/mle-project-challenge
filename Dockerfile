FROM python:3.9-slim

WORKDIR /usr/src/app

# install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy only the necessary directories and files for the API to work
COPY api/ ./api/
COPY common/ ./common/
COPY data/zipcode_demographics.csv ./data/

EXPOSE 8000

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
