# Используйте базовый образ Python
FROM python:3.11

# Установите зависимости
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app


CMD ["python", "-u", "crm.py"]
