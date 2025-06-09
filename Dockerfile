FROM python:3.11-slim-bullseye

WORKDIR /app
COPY . /app

ENV PYTHONPATH="/app"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--lifespan", "on"]