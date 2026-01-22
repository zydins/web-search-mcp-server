FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies required for building and playwright
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only to save space)
RUN playwright install --with-deps chromium

COPY . .

# Default port
ENV PORT=8000

# Expose the port defined by the environment variable
EXPOSE $PORT

# Run the server using python directly so it picks up the PORT env var logic
CMD ["python", "server.py"]
