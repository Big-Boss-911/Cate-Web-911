"""
Health check and root views for Railway deployment.
Source: source/web_service/pequeroku/health.py
"""
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

_INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PequeRoku</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 600px; margin: 80px auto; padding: 0 20px; color: #1a1a1a; }}
    h1   {{ font-size: 2rem; margin-bottom: 0.25rem; }}
    p    {{ color: #555; margin-top: 0; }}
    ul   {{ padding-left: 1.2rem; line-height: 2; }}
    a    {{ color: #0070f3; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .badge {{ display: inline-block; background: #22c55e; color: #fff;
              font-size: 0.75rem; font-weight: 600; padding: 2px 8px;
              border-radius: 999px; vertical-align: middle; margin-left: 8px; }}
  </style>
</head>
<body>
  <h1>PequeRoku <span class="badge">running</span></h1>
  <p>Cloud container platform — application is running successfully.</p>
  <ul>
    <li><a href="/admin/">Admin panel</a></li>
    <li><a href="/api/schema/swagger-ui/">API docs (Swagger UI)</a></li>
    <li><a href="/api/schema/redoc/">API docs (ReDoc)</a></li>
    <li><a href="/health">Health check</a></li>
    <li><a href="/readiness">Readiness check</a></li>
  </ul>
</body>
</html>"""


@require_http_methods(["GET", "HEAD"])
def index(request):
    """Root view — returns HTTP 200 with a simple landing page.

    Avoids the redirect chain (/ → /admin/ → /admin/login/) that can confuse
    health probes and makes the API surface immediately discoverable.
    """
    return HttpResponse(_INDEX_HTML, content_type="text/html; charset=utf-8")


@require_http_methods(["GET"])
def health(request):
    """Health check endpoint for Railway/load balancers.
    
    Returns 200 OK if Django is operational and database is accessible.
    """
    try:
        from django.db import connection
        connection.ensure_connection()
        return JsonResponse({"status": "ok", "service": "pequeroku-web"})
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=503
        )


@require_http_methods(["GET"])
def readiness(request):
    """Readiness check - confirms service is ready for traffic.
    
    More comprehensive than health check, verifies all dependencies.
    """
    try:
        from django.db import connection
        from django.core.cache import cache
        
        # Check database
        connection.ensure_connection()
        
        # Check Redis/cache
        cache.set("readiness_check", "ok", 1)
        if cache.get("readiness_check") != "ok":
            raise Exception("Cache unavailable")
        
        return JsonResponse({
            "status": "ready",
            "service": "pequeroku-web",
            "checks": {
                "database": "ok",
                "cache": "ok"
            }
        })
    except Exception as e:
        return JsonResponse(
            {"status": "not_ready", "message": str(e)},
            status=503
        )
