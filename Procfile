Procfile
web: cd source/web_service && python manage.py migrate && python manage.py collectstatic --no-input && gunicorn pequeroku.asgi:application -k uvicorn.workers.UvicornWorker -w ${WORKERS:-4} -b 0.0.0.0:${PORT:-8000} --graceful-timeout 30 --timeout 600
