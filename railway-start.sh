#!/usr/bin/env bash
set -euo pipefail

# Railway entrypoint — runs inside the Docker container where WORKDIR=/app
# (i.e. the contents of source/web_service are already at /app)

echo "[railway-start] Running Django migrations..."
python manage.py migrate

echo "[railway-start] Collecting static files..."
python manage.py collectstatic --no-input

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "[railway-start] Creating superuser ${DJANGO_SUPERUSER_USERNAME}..."
  python manage.py createsuperuser --noinput || true
else
  echo "[railway-start] Skipping superuser creation (DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD not set)"
fi

echo "[railway-start] Starting background workers..."
(sleep 5; python manage.py reconcile_containers --loop --interval "${RECONCILE_INTERVAL:-30}") &
(sleep 5; python manage.py prewarm_pool      --loop --interval "${PREWARM_INTERVAL:-30}")    &
(sleep 5; python manage.py run_worker        --loop --interval "${RUN_WORKER_INTERVAL:-5}")  &
(sleep 5; python manage.py reap_expired      --loop --interval "${REAP_INTERVAL:-30}")       &

echo "[railway-start] Starting Gunicorn with Uvicorn workers on port ${PORT:-8000}..."
exec gunicorn pequeroku.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  -w "${WORKERS:-4}" \
  -b "0.0.0.0:${PORT:-8000}" \
  --graceful-timeout 30 \
  --timeout 600 \
  --access-logfile - \
  --error-logfile -
