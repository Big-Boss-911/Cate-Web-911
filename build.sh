#!/usr/bin/env bash
set -euo pipefail

# Railway build script for web_service
# Runs during Railway deployment build phase

cd source/web_service

echo "[build] Installing Python dependencies..."
pip install --upgrade pip poetry
poetry config virtualenvs.create false
poetry install --no-root --no-interaction --no-ansi

echo "[build] Verifying Django setup..."
python manage.py check

echo "[build] Build completed successfully"
