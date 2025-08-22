FROM python:3.12-slim-bookworm

# Create non-root user first
RUN groupadd -r flask-api && useradd -r -g flask-api flask-api

WORKDIR /flask-api/

# Copy requirements first for better layer caching
COPY requirements.txt ./

# Update package lists and install dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/log/flask && \
    chown -R flask-api:flask-api /flask-api /var/log/flask

# Copy application code
COPY app.py ./
RUN chmod +x app.py && chown flask-api:flask-api app.py

# Switch to non-root user
USER flask-api

# Use environment variables for configuration
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Use CMD instead of ENTRYPOINT for flexibility
CMD ["python", "app.py"]