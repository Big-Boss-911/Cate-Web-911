# PequeRoku — Railway Deployment Report

---

## 1. Project Type

Multi-service monorepo. The Railway deployment targets only the **web service** (Django backend).

---

## 2. Framework

**Django 5.2+** with:
- **Django REST Framework** — REST API
- **Django Channels 4** — WebSocket support
- **drf-spectacular** — OpenAPI schema

Evidence: `source/web_service/pyproject.toml` line 10–11:
```
django = {extras = ["async"], version = "^5.2.6"}
djangorestframework = "^3.16.1"
```

---

## 3. Runtime

**Python 3.13** (Docker image: `python:3.13-slim`)

Evidence: `Dockerfile.railway` line 1:
```
FROM python:3.13-slim
```

Constraint in `pyproject.toml`:
```
python = "^3.11"
```

---

## 4. Package Manager

**Poetry** for Python dependencies.
**pnpm 9.15.0** for the React frontend (not included in Railway deployment).

Evidence: `source/web_service/pyproject.toml` build-system section.

---

## 5. Build Command

```bash
# Dockerfile.railway handles the build:
pip install --upgrade pip && pip install poetry
poetry config virtualenvs.create false
poetry install --no-root --no-interaction --no-ansi
```

---

## 6. Start Command

```bash
bash /app/railway-start.sh
```

Which runs:
1. `python manage.py migrate`
2. `python manage.py collectstatic --no-input`
3. Optionally `python manage.py createsuperuser --noinput`
4. Background management commands: `reconcile_containers`, `prewarm_pool`, `run_worker`, `reap_expired`
5. `gunicorn pequeroku.asgi:application -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:${PORT:-8000}`

---

## 7. Complete Environment Variables

| Variable | Required | Default | Source File | Purpose |
|---|---|---|---|---|
| `DATABASE_URL` | **Required** | — | `settings.py:145` | PostgreSQL connection string (Railway plugin) |
| `DB_NAME` | Required if no `DATABASE_URL` | — | `settings.py:164` | PostgreSQL database name |
| `DB_USER` | Required if no `DATABASE_URL` | — | `settings.py:165` | PostgreSQL user |
| `DB_PASSWORD` | Required if no `DATABASE_URL` | — | `settings.py:166` | PostgreSQL password |
| `DB_HOST` | Required if no `DATABASE_URL` | — | `settings.py:167` | PostgreSQL host |
| `DB_PORT` | Required if no `DATABASE_URL` | `5432` | `settings.py:168` | PostgreSQL port |
| `REDIS_URL` | **Required** | `redis://redis:6379/1` | `settings.py:42` | Redis connection string |
| `SECRET_KEY` | **Required** | `thisisnotasecretkey` | `settings.py:9` | Django secret key |
| `ALLOWED_HOSTS` | **Required** | `""` | `settings.py:23` | Comma-separated allowed hostnames |
| `INTERNAL_HOSTS` | Optional | `web,localhost,127.0.0.1` | `settings.py:18` | Internal service hostnames |
| `DEBUG` | Optional | `true` | `settings.py:10` | Django debug mode (set `false` in production) |
| `HTTP_PORT` | Optional | `80` | `settings.py:31` | External port for CSRF trusted origins |
| `PORT` | Optional | `8000` | `railway-start.sh` | Gunicorn listen port |
| `WORKERS` | Optional | `4` | `railway-start.sh` | Gunicorn worker count |
| `LOG_LEVEL` | Optional | `INFO` | `settings.py:196` | App logging level |
| `TZ` | Optional | `UTC` | `settings.py:179` | Timezone |
| `REDIS_PREFIX` | Optional | `web_service:` | `settings.py:46` | Redis key prefix |
| `PLATFORM_API_THROTTLE_RATE` | Optional | `120/min` | `settings.py:128` | API rate limit |
| `RECONCILE_INTERVAL` | Optional | `30` | `railway-start.sh` | Container reconcile interval (seconds) |
| `PREWARM_INTERVAL` | Optional | `30` | `railway-start.sh` | Pool prewarm interval (seconds) |
| `RUN_WORKER_INTERVAL` | Optional | `5` | `railway-start.sh` | Worker run interval (seconds) |
| `REAP_INTERVAL` | Optional | `30` | `railway-start.sh` | Expired task reap interval (seconds) |
| `DJANGO_SETTINGS_MODULE` | Optional | `pequeroku.settings` | `settings.py` | Django settings module |
| `DJANGO_SUPERUSER_USERNAME` | Optional | — | `railway-start.sh` | Auto-create admin username |
| `DJANGO_SUPERUSER_PASSWORD` | Optional | — | `railway-start.sh` | Auto-create admin password |
| `DJANGO_SUPERUSER_EMAIL` | Optional | — | `railway-start.sh` | Auto-create admin email |
| `START_FROM_LATEST` | Optional | `true` | `.env.railway` | Resume from latest VM snapshot |
| `MAX_CONCURRENT_TASKS` | Optional | `2` | `.env.railway` | Max concurrent agent tasks |
| `ANTHROPIC_API_KEY` | Optional | — | `.env.railway` | Anthropic Claude API key |
| `OPENAI_API_KEY` | Optional | — | `.env.railway` | OpenAI API key |
| `OPEN_ROUTER_API_KEY` | Optional | — | `.env.railway` | OpenRouter API key |
| `GOOGLE_GENERATIVE_AI_API_KEY` | Optional | — | `.env.railway` | Google AI API key |
| `OPENAI_LIKE_API_KEY` | Optional | — | `.env.railway` | OpenAI-compatible provider key |

---

## 8. Railway Files Created

| File | Description |
|---|---|
| `railway.json` | Builder: Dockerfile.railway. Deploy: `bash /app/railway-start.sh` |
| `Dockerfile.railway` | Production image based on `python:3.13-slim` |
| `railway-start.sh` | Container startup: migrate → collectstatic → workers → gunicorn |
| `build.sh` | Build-phase script (Poetry install + django check) |
| `health-check.sh` | External health probe script |
| `.env.railway` | Environment variable template for Railway dashboard |
| `nixpacks.toml` | Nixpacks configuration (fallback if Dockerfile not used) |
| `RAILWAY_DEPLOYMENT.md` | Human-readable deployment guide |
| `source/web_service/pequeroku/health.py` | Health + readiness endpoint views |

---

## 9. Railway Files Modified

| File | Change |
|---|---|
| `source/web_service/pequeroku/urls.py` | Added `/health` and `/readiness` URL routes |
| `source/web_service/pequeroku/settings.py` | Added `DATABASE_URL` parsing, `LOG_LEVEL`, `TZ`, `REDIS_URL` env support |
| `source/web_service/entrypoint.sh` | Fixed hardcoded port `8000` → `${PORT:-8000}` |
| `Procfile` | Fixed invalid file (had "Procfile" as first line, not a valid process definition) |
| `nixpacks.toml` | Fixed invalid file (was a bash script, not TOML) |
| `RAILWAY_DEPLOYMENT.md` | Fixed invalid file (was a bash script, not markdown) |
| `Dockerfile.railway` | Fixed CMD reference: now copies `railway-start.sh` into image |

---

## 10. Problems Fixed

### Problem 1: `railway-start.sh` not present in Docker image
**Evidence:** `Dockerfile.railway` set `CMD ["bash", "/app/entrypoint.sh"]` but `railway.json` overrode with `bash railway-start.sh`. The file was never `COPY`-d into the image.
**Fix:** Added `COPY railway-start.sh /app/railway-start.sh` in `Dockerfile.railway`. Updated CMD to `["bash", "/app/railway-start.sh"]`. Updated `railway.json` startCommand to `bash /app/railway-start.sh`.

### Problem 2: `railway-start.sh` contained invalid `cd source/web_service`
**Evidence:** Inside the Docker container, `WORKDIR` is `/app` which already contains the `web_service` contents. Running `cd source/web_service` would fail with "No such file or directory".
**Fix:** Rewrote `railway-start.sh` to omit the `cd` and add all background worker commands (which were missing).

### Problem 3: `Procfile` had "Procfile" as its first line
**Evidence:** Line 1 of `Procfile` was the literal text `Procfile` instead of a process definition. This makes it unparseable by Railway/Heroku.
**Fix:** Rewrote `Procfile` to contain only valid process definitions.

### Problem 4: `nixpacks.toml` was a bash script
**Evidence:** File started with `#!/usr/bin/env bash` and contained shell commands. TOML syntax is required.
**Fix:** Rewrote as valid TOML with `[phases.setup]`, `[phases.install]`, and `[start]` sections.

### Problem 5: `RAILWAY_DEPLOYMENT.md` was a bash script
**Evidence:** File started with `#!/usr/bin/env bash`. A `.md` file should be Markdown.
**Fix:** Rewrote as a proper Markdown deployment guide.

### Problem 6: No `DATABASE_URL` support in `settings.py`
**Evidence:** `settings.py` only read individual `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` variables. Railway PostgreSQL plugin provides a single `DATABASE_URL` connection string.
**Fix:** Added `DATABASE_URL` parsing with `urllib.parse.urlparse`. Falls back to individual `DB_*` variables if `DATABASE_URL` is not set.

### Problem 7: Hardcoded port `8000` in `entrypoint.sh`
**Evidence:** `entrypoint.sh` line 42 used literal `8000` instead of `${PORT:-8000}`.
**Fix:** Changed to `-b "0.0.0.0:${PORT:-8000}"` to respect Railway's `PORT` environment variable.

---

## 11. Remaining Issues

### VM Service not deployable on Railway
**Evidence:** `source/vm_service/` requires QEMU/KVM (`apt install qemu-system-x86`). Railway containers do not provide nested virtualization / KVM access. This service must run on a dedicated host with bare-metal or KVM-enabled virtualization.

### React Frontend requires separate deployment
**Evidence:** `source/front-react/` is a Vite SPA. It should be deployed as a static site (Vercel, Netlify, or Railway static deployment) with `VITE_API_URL` pointing to the Django web service URL.

### Background workers share the web process
**Evidence:** `railway-start.sh` runs `reconcile_containers`, `prewarm_pool`, `run_worker`, and `reap_expired` as background processes (`&`) inside the same container as Gunicorn. On Railway free tier, this works but is not horizontally scalable. For production, each worker should be a separate Railway service.

---

## 12. Evidence from Source Code

- Framework: `source/web_service/pyproject.toml` — `django = {extras = ["async"], version = "^5.2.6"}`
- ASGI: `source/web_service/pequeroku/asgi.py` — `ProtocolTypeRouter` with HTTP + WebSocket
- Health endpoints: `source/web_service/pequeroku/health.py` — `/health`, `/readiness`
- URL registration: `source/web_service/pequeroku/urls.py` — `path("health", health, ...)`, `path("readiness", readiness, ...)`
- PORT support: `railway-start.sh` — `-b "0.0.0.0:${PORT:-8000}"`
- HOST binding: `railway-start.sh` — `-b "0.0.0.0:..."`
- DATABASE_URL: `source/web_service/pequeroku/settings.py` — `urllib.parse.urlparse(DATABASE_URL)`

---

## 13. Evidence from Build Logs

NOT VERIFIED — Railway build has not been triggered from this environment. The Dockerfile has been validated for correctness by inspection.

---

## 14. Evidence from Runtime Logs

NOT VERIFIED — The application requires PostgreSQL and Redis which are not available in this Replit environment. Runtime verification must be performed after deploying to Railway with the required services linked.
