"""
Health check view for Railway deployment
Source: source/web_service/pequeroku/health.py
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


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
