FROM python:3.12-slim

WORKDIR /app

COPY . /app

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python3", "app.py"]