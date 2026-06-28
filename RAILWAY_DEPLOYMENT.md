# PequeRoku Railway Deployment Guide

## 1. Environment Variables

Copy `.env.railway` as a reference and set these in your Railway project dashboard.

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | **Required** | — | Railway PostgreSQL plugin URL |
| `REDIS_URL` | **Required** | — | Railway Redis plugin URL |
| `SECRET_KEY` | **Required** | — | Django secret key |
| `ALLOWED_HOSTS` | **Required** | — | Your Railway domain (e.g. `myapp.up.railway.app`) |
| `DEBUG` | Optional | `false` | Set to `false` in production |
| `LOG_LEVEL` | Optional | `WARNING` | Logging level |
| `TZ` | Optional | `UTC` | Timezone (e.g. `Asia/Amman`) |
| `WORKERS` | Optional | `4` | Gunicorn worker count |
| `PORT` | Optional | `8000` | Port the app listens on |
| `DJANGO_SUPERUSER_USERNAME` | Optional | — | Auto-create admin user |
| `DJANGO_SUPERUSER_PASSWORD` | Optional | — | Auto-create admin user |
| `DJANGO_SUPERUSER_EMAIL` | Optional | — | Auto-create admin user |
| `ANTHROPIC_API_KEY` | Optional | — | Anthropic API key |
| `OPENAI_API_KEY` | Optional | — | OpenAI API key |
| `OPEN_ROUTER_API_KEY` | Optional | — | OpenRouter API key |
| `GOOGLE_GENERATIVE_AI_API_KEY` | Optional | — | Google AI API key |
| `OPENAI_LIKE_API_KEY` | Optional | — | OpenAI-compatible provider key |
| `START_FROM_LATEST` | Optional | `true` | Resume from latest state |
| `MAX_CONCURRENT_TASKS` | Optional | `2` | Max concurrent agent tasks |

## 2. Build Command

Automatically detected from `Dockerfile.railway`:
- Installs system dependencies (gcc, libpq-dev, etc.)
- Installs Poetry and all Python dependencies
- Copies `source/web_service` into `/app`

## 3. Start Command

Defined in `railway.json` and executed by `railway-start.sh`:
1. Runs Django migrations: `python manage.py migrate`
2. Collects static files: `python manage.py collectstatic --no-input`
3. Optionally creates a Django superuser
4. Starts background workers (reconcile, prewarm, run_worker, reap_expired)
5. Starts Gunicorn with Uvicorn workers: `gunicorn pequeroku.asgi:application`

## 4. Health Checks

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness probe — verifies database connectivity |
| `GET /readiness` | Readiness probe — verifies database + Redis |

## 5. Database

- Use the Railway **PostgreSQL** plugin
- Set `DATABASE_URL` (automatically provided by the plugin when linked)
- Migrations run automatically at startup

## 6. Cache (Redis)

- Use the Railway **Redis** plugin
- Set `REDIS_URL` (automatically provided by the plugin when linked)
- Used for Django channels, sessions, and rate limiting

## 7. Static Files

- Collected to `/app/staticfiles/` at startup
- Served by Django in production mode

## 8. Files Created / Modified for Railway

| File | Status | Purpose |
|---|---|---|
| `railway.json` | Created | Deployment configuration (builder + start command) |
| `Procfile` | Created | Fallback process definition |
| `Dockerfile.railway` | Created | Production Docker image |
| `railway-start.sh` | Created | Container startup script |
| `build.sh` | Created | Build-phase script |
| `health-check.sh` | Created | External health check helper |
| `.env.railway` | Created | Environment variable reference template |
| `nixpacks.toml` | Created | Nixpacks build configuration |
| `source/web_service/pequeroku/health.py` | Created | Health/readiness endpoint views |
| `source/web_service/pequeroku/urls.py` | Modified | Added `/health` and `/readiness` routes |
| `source/web_service/pequeroku/settings.py` | Modified | Added `DATABASE_URL`, `LOG_LEVEL`, `TZ`, `PORT` support |
| `source/web_service/entrypoint.sh` | Modified | Fixed hardcoded port 8000 → `${PORT:-8000}` |

## 9. Deploying to Railway

1. Connect your GitHub repository to Railway
2. Set the required environment variables in the Railway dashboard
3. Add a PostgreSQL plugin and link it (sets `DATABASE_URL`)
4. Add a Redis plugin and link it (sets `REDIS_URL`)
5. Enable automatic deployments on push to `main`
6. Push changes to trigger the first deployment

## 10. Notes

- The VM service (`source/vm_service`) requires QEMU/KVM and is not included in this Railway deployment. It must run on a separate host with virtualization support.
- The MCP service (`source/mcp_service`) can be deployed as a separate Railway service pointing to the web service API.
- The React frontend (`source/front-react`) is a separate SPA and should be deployed to a static host (e.g. Vercel, Netlify, Railway static site) pointing its API calls at the web service URL.
