#!/usr/bin/env bash
# Health check script for Railway
# Tests if the web service is responding

max_attempts=5
attempt=0

while [ $attempt -lt $max_attempts ]; do
  if curl -sf http://localhost:${PORT:-8000}/api/v1/health > /dev/null 2>&1; then
    echo "✓ Health check passed"
    exit 0
  fi
  
  attempt=$((attempt + 1))
  if [ $attempt -lt $max_attempts ]; then
    echo "⏳ Health check attempt $attempt/$max_attempts failed, retrying..."
    sleep 2
  fi
done

echo "✗ Health check failed after $max_attempts attempts"
exit 1
