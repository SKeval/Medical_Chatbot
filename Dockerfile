FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (prevents many pip failures)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app
COPY . .

# Run app
CMD ["python", "app.py"]