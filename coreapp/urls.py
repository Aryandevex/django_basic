"""
coreapp/urls.py
----------------
Template-based views only (auth, CRUD pages, landing page).
The DRF REST API router lives in coreapp/api_urls.py.
"""
from django.urls import path
from .views import (
    MemberListView, MemberCreateView, MemberUpdateView, MemberDeleteView,
    TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView,
    ProjectListView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView,
    MemberLoginView, MemberLogoutView, DashboardView, IndexView,
    AdminDashboardView,
)

urlpatterns = [
    # ── Home / Landing page ────────────────────────────────────
    path('', IndexView.as_view(), name='index'),

    # ── Auth ──────────────────────────────────────────────────
    path('login/',           MemberLoginView.as_view(),    name='member-login'),
    path('logout/',          MemberLogoutView.as_view(),   name='member-logout'),
    path('dashboard/',       DashboardView.as_view(),      name='dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),

    # ── Member CRUD (templates) ───────────────────────────────
    path('members/',                 MemberListView.as_view(),   name='member-list'),
    path('members/create/',          MemberCreateView.as_view(), name='member-create'),
    path('members/<int:pk>/edit/',   MemberUpdateView.as_view(), name='member-edit'),
    path('members/<int:pk>/delete/', MemberDeleteView.as_view(), name='member-delete'),

    # ── Task CRUD (templates) ─────────────────────────────────
    path('tasks/',                 TaskListView.as_view(),   name='task-list'),
    path('tasks/create/',          TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/edit/',   TaskUpdateView.as_view(), name='task-edit'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),

    # ── Project CRUD (templates) ──────────────────────────────
    path('projects/',                 ProjectListView.as_view(),   name='project-list'),
    path('projects/create/',          ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/edit/',   ProjectUpdateView.as_view(), name='project-edit'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project-delete'),
]
