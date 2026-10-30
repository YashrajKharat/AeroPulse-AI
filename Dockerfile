# AeroPulse AI - Container Definition
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY . .

# Environment defaults
ENV PYTHONUNBUFFERED=1
ENV AEROPULSE_PORT=8050
ENV AEROPULSE_DB=warehouse/flight_warehouse.duckdb

# Expose web server port
EXPOSE 8050

# Run Phase 8 Dashboard Server
CMD ["python", "-u", "run_all.py", "--phase", "8"]
