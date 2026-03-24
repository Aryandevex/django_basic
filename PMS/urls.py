"""
URL configuration for PMS project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Template views: landing, auth, member CRUD, task CRUD
    path('', include('coreapp.urls')),

    # REST API only (DRF router) – no overlap with template URLs
    path('api/', include('coreapp.api_urls')),

    # DRF Browsable API login/logout
    path('api-auth/', include('rest_framework.urls')),
]
