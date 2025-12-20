

from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse
import numpy as np
import os
import joblib
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

# Настройка логов
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Счётчик запросов
requests_total = Counter("requests_total", "Total number of requests", ["endpoint"])

# Гистограмма для латентности (время выполнения запроса)
request_latency = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

app = FastAPI()
VERSION = os.getenv("MODEL_VERSION", "v1.0.0")
# Загружаем модель (предварительно сохрани её через joblib.dump)
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
model = joblib.load(MODEL_PATH)

@app.get("/health")
def health():
    start = time.time()
    requests_total.labels(endpoint="/health").inc()
    logger.info("Зашли в Health")
    response = {"status": "ok", "version": VERSION}
    request_latency.labels(endpoint="/health").observe(time.time() - start)
    return response

@app.get("/ui", response_class=HTMLResponse)
def ui_form():
    start = time.time()
    requests_total.labels(endpoint="/ui").inc()
    logger.info("Зашли в UI")
    html_content = '''
    <html>
        <head>
            <title>ML Wine Prediction UI</title>
        </head>
        <body>
            <h2>Введите значения признаков для предсказания</h2>
            <form action="/predict" method="post">
                <label for="request">Фичи (через запятую):</label><br>
                <input type="text" id="x" name="request" value="1.0,2.0,3.0"><br><br>
                <input type="submit" value="Отправить">
            </form>
        </body>
    </html>
    '''
    request_latency.labels(endpoint="/ui").observe(time.time() - start)
    return HTMLResponse(content=html_content)

@app.post("/predict")
def predict(request: str = Form(...)):
    start = time.time()
    requests_total.labels(endpoint="/predict").inc()
    features = [float(val.strip()) for val in request.split(',')]
    logger.info(f"Начинаю предикт для интпута: {features}")
    X = np.array(features).reshape(1, -1)
    y_pred = model.predict(X)[0]
    logger.info(f"Получен предикт: {y_pred}")
    response = {
        "status": "ok",
        "prediction": int(y_pred),
        "version": VERSION
    }
    request_latency.labels(endpoint="/predict").observe(time.time() - start)
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/sleep")
def health():
    start = time.time()
    requests_total.labels(endpoint="/sleep").inc()
    logger.info("Зашли в Sleep")
    time.sleep(2)
    response = {"status": "ok", "sleep": "ok"}
    request_latency.labels(endpoint="/sleep").observe(time.time() - start)
    return response

