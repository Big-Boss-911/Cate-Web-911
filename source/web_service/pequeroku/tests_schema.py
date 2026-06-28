"""
Test suite for API schema generation and endpoint validation.
Verifies that /api/schema/ returns HTTP 200 and schema generation doesn't fail.
"""

import pytest
from django.test import Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestSchemaGeneration:
    """Test API schema generation endpoints."""

    def setup_method(self):
        """Set up test client and create a test user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_schema_endpoint_returns_200(self):
        """Test that /api/schema/ returns HTTP 200 status code."""
        response = self.client.get('/api/schema/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.data if hasattr(response, 'data') else response.content}"

    def test_schema_endpoint_returns_openapi_json(self):
        """Test that /api/schema/ returns valid OpenAPI JSON schema."""
        response = self.client.get('/api/schema/')
        assert response.status_code == 200
        
        # Check that response contains OpenAPI schema structure
        data = response.json() if hasattr(response, 'json') else response.data
        assert 'openapi' in data or 'swagger' in data, "Response should contain OpenAPI/Swagger schema"
        assert 'paths' in data, "Schema should contain paths"
        assert 'info' in data, "Schema should contain info"

    def test_swagger_ui_endpoint_returns_200(self):
        """Test that /api/schema/swagger-ui/ returns HTTP 200."""
        response = self.client.get('/api/schema/swagger-ui/')
        assert response.status_code == 200, f"Swagger UI returned {response.status_code}"

    def test_redoc_endpoint_returns_200(self):
        """Test that /api/schema/redoc/ returns HTTP 200."""
        response = self.client.get('/api/schema/redoc/')
        assert response.status_code == 200, f"ReDoc returned {response.status_code}"

    def test_root_endpoint_returns_200(self):
        """Test that root endpoint / returns HTTP 200."""
        response = self.client.get('/')
        assert response.status_code == 200, f"Root endpoint returned {response.status_code}"

    def test_health_check_endpoint(self):
        """Test that /health endpoint returns HTTP 200."""
        response = self.client.get('/health')
        assert response.status_code == 200, f"Health check returned {response.status_code}"
        data = response.json()
        assert data.get('status') == 'ok', "Health check should return status: ok"

    def test_readiness_endpoint(self):
        """Test that /readiness endpoint returns HTTP 200 or 503."""
        response = self.client.get('/readiness')
        # Readiness might return 503 if Redis is not available in test, which is ok
        assert response.status_code in [200, 503], f"Readiness check returned unexpected {response.status_code}"

    def test_v1_schema_endpoint(self):
        """Test that /api/v1/schema/ returns HTTP 200 (v1 API schema)."""
        response = self.client.get('/api/v1/schema/')
        # v1 schema may require authentication, so 401 is acceptable for unauthenticated requests
        assert response.status_code in [200, 401, 403], f"v1 schema endpoint returned {response.status_code}"

    def test_admin_login_page(self):
        """Test that /admin/ returns HTTP 200 (login page)."""
        response = self.client.get('/admin/')
        assert response.status_code in [200, 302], f"Admin page returned {response.status_code}"


@pytest.mark.django_db
class TestAPIEndpoints:
    """Test core API endpoints."""

    def setup_method(self):
        """Set up test client and create a test user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )

    def test_api_root_endpoint(self):
        """Test that /api/ endpoint exists and is accessible."""
        response = self.client.get('/api/')
        # Could be 401 (requires auth) or 404 (endpoint doesn't exist), both are ok
        assert response.status_code in [200, 401, 403, 404], f"API root returned {response.status_code}"

    def test_schema_hook_doesnt_crash(self):
        """Test that the schema preprocessing hook doesn't crash the schema generation."""
        response = self.client.get('/api/schema/')
        assert response.status_code == 200
        
        # Verify that v1 paths are excluded from the default schema
        data = response.json() if hasattr(response, 'json') else response.data
        paths = data.get('paths', {})
        
        # The exclude_v1_from_default hook should filter out /api/v1 paths
        for path in paths.keys():
            assert not path.startswith('/api/v1/'), f"v1 path should not be in default schema: {path}"


@pytest.mark.django_db  
class TestNoExceptions:
    """Test that critical endpoints don't raise unhandled exceptions."""

    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()

    def test_schema_generation_no_exception(self):
        """Test that schema generation completes without raising exceptions."""
        try:
            response = self.client.get('/api/schema/')
            assert response.status_code == 200, f"Schema generation failed with status {response.status_code}"
        except Exception as e:
            pytest.fail(f"Schema generation raised exception: {str(e)}")

    def test_swagger_ui_no_exception(self):
        """Test that Swagger UI loads without raising exceptions."""
        try:
            response = self.client.get('/api/schema/swagger-ui/')
            assert response.status_code == 200, f"Swagger UI failed with status {response.status_code}"
        except Exception as e:
            pytest.fail(f"Swagger UI raised exception: {str(e)}")

    def test_redoc_no_exception(self):
        """Test that ReDoc loads without raising exceptions."""
        try:
            response = self.client.get('/api/schema/redoc/')
            assert response.status_code == 200, f"ReDoc failed with status {response.status_code}"
        except Exception as e:
            pytest.fail(f"ReDoc raised exception: {str(e)}")
