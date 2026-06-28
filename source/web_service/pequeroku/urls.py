from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from pequeroku.health import health, index, readiness

urlpatterns = [
    # Root — returns HTTP 200 directly; no redirect chain, no 404.
    path("", index, name="root"),

    # Health check endpoints for Railway/load balancers
    path("health", health, name="health"),
    path("readiness", readiness, name="readiness"),
    
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/", include("platform_api.urls")),
    path("api/account/", include("platform_api.account_urls")),
    path("api/", include("vm_manager.urls")),
    path("admin/", admin.site.urls),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
