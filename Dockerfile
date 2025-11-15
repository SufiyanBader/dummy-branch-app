# Stage 1: Build - Install dependencies
FROM python:3.10-slim-bookworm AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production - Copy app and dependencies
FROM python:3.10-slim-bookworm
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app/requirements.txt .
COPY app.py .
COPY app_test.py .

# Environment var for Python
ENV PYTHONUNBUFFERED=1

# Expose the port Gunicorn will run on
EXPOSE 8080

# Command to run the app using Gunicorn (production server)
# It binds to port 8080, which matches our docker-compose.yml
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
