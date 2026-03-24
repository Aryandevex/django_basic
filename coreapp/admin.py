"""
coreapp/admin.py
-----------------
Registers Project and Member with the Django Admin panel.
Allows superuser to manage records via the /admin/ interface in addition to the API.
"""
from django.contrib import admin
from .models import Project, Member, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_username', 'role', 'project', 'phone', 'created_at']
    search_fields = ['user__username', 'project__name']
    list_filter = ['role', 'project']
    ordering = ['-created_at']

    @admin.display(description='Username')
    def get_username(self, obj):
        return obj.user.username


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'assigned_to', 'project', 'status', 'due_date', 'created_at']
    search_fields = ['title', 'assigned_to__user__username']
    list_filter = ['status', 'project']
    ordering = ['-created_at']
