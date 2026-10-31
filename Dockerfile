FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-chi-sim && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV TRACKER_HOST=0.0.0.0 TRACKER_DATA=/app/data PYTHONUNBUFFERED=1
EXPOSE 8765
CMD ["python","app.py"]
