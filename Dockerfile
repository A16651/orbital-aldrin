# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better cache
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose the default port
EXPOSE 8000

# Run using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
