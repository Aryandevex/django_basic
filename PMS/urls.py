"""
URL configuration for PMS project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # All template views: landing, auth, member CRUD, task CRUD
    path('', include('coreapp.urls')),
]
