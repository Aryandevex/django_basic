"""
coreapp/api_urls.py
--------------------
DRF Router – only used under the /api/ prefix in PMS/urls.py.
Keeps the REST API completely separate from template-based views.
"""
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, MemberViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'members',  MemberViewSet,  basename='member-api')

urlpatterns = router.urls
