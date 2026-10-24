# Use a lightweight official Python image
FROM python:3.13-slim

# Install system dependencies (git is useful if your script needs to check git status or diffs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Upgrade pip and install required Python packages directly
# (Using groq for the LLM API and requests/httpx if needed)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir groq requests

# Copy your Python script into the container's working directory
COPY main.py /app/main.py

# Set the entrypoint so Python executes your script when the container runs
ENTRYPOINT ["python", "/app/main.py"]