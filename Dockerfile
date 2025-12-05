# ==========================================
# Stage 1: Builder (Compiling dependencies)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy dependency file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies into a specific location (/install)
# --prefix tells pip to install libraries here so we can copy them later
RUN pip install --default-timeout=1000 --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# Stage 2: Runtime (Minimal final image)
# ==========================================
FROM python:3.11-slim

# CRITICAL: Set timezone to UTC universally
ENV TZ=UTC

WORKDIR /app

# Install system dependencies
# - cron: Required for the background task
# - tzdata: Required to configure timezone
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    # Clean up cache to reduce image size
    rm -rf /var/lib/apt/lists/*

# Configure System Timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy Python dependencies from the builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY app /app/app

# Copy Keys (Required for decryption inside the container)
# Note: These must exist in your project root
COPY student_private.pem /app/
COPY student_public.pem /app/
COPY instructor_public.pem /app/

# --- Cron Job Setup ---
# --- Cron Job Setup ---
COPY cron/2fa-cron /etc/cron.d/2fa-cron
COPY scripts /app/scripts

# 1. Fix Windows line endings
# 2. Create the /cron directory (CRITICAL STEP)
# 3. Create the log file
# 4. Set permissions and register cron
RUN sed -i 's/\r$//' /etc/cron.d/2fa-cron && \
    mkdir -p /cron && \
    touch /cron/last_code.txt && \
    chmod 0644 /etc/cron.d/2fa-cron && \
    chmod 666 /cron/last_code.txt && \
    crontab /etc/cron.d/2fa-cron

# 1. Set permissions on cron file (must be 0644)
# 2. Register the cron job
# 3. Create persistent volume mount points
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron && \
    mkdir -p /data /cron && \
    chmod 755 /data /cron

# Expose the API port
EXPOSE 8080

# Add this to your Dockerfile to ensure the folder exists
RUN mkdir -p /cron
# Start Command:
# 1. Starts the cron daemon in the background
# 2. Starts the FastAPI server (uvicorn) in the foreground
CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8080