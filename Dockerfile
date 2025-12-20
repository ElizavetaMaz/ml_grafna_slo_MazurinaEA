# Базовый образ
FROM python:3.10-slim

# Переменные окружения
ENV MODEL_PATH=/app/models/model.pkl \
    MODEL_VERSION=v1.0.0

# Рабочая директория
WORKDIR /app

# Копирование зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Точка входа
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]