#!/usr/bin/env bash
set -euo pipefail

# Railway entrypoint - runs migrations and starts the web service
cd source/web_service

echo "[railway-start] Running Django migrations..."
python manage.py migrate

echo "[railway-start] Collecting static files..."
python manage.py collectstatic --no-input

echo "[railway-start] Starting Gunicorn with Uvicorn workers..."
exec gunicorn pequeroku.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  -w ${WORKERS:-4} \
  -b 0.0.0.0:${PORT:-8000} \
  --graceful-timeout 30 \
  --timeout 600 \
  --access-logfile - \
  --error-logfile -
