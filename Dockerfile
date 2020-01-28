FROM python:3.7-slim-buster

WORKDIR /flask-api/
COPY requirements.txt ./
COPY app.py ./

RUN apt update -y && \ 
    apt upgrade -y && \
    useradd flask-api && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x app.py

USER flask-api

ENTRYPOINT ["/flask-api/app.py"]