"""
coreapp/permissions.py
-----------------------
Custom DRF permission classes for role-based API access.

Use these in ViewSets that need role-level access (not just admin-level).
Admins always pass all role checks.

Usage in a ViewSet:
    from .permissions import IsTeamLead

    class SomeViewSet(ModelViewSet):
        permission_classes = [IsAuthenticated, IsTeamLead]
"""
from rest_framework.permissions import BasePermission


class _RolePermission(BasePermission):
    """Base class for role-based DRF permissions."""
    allowed_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Superuser bypasses all role checks
        if request.user.is_superuser:
            return True
        try:
            return request.user.member.role in self.allowed_roles
        except AttributeError:
            return False


class IsTeamLead(_RolePermission):
    """Grants access to Team Lead role (+ admins)."""
    allowed_roles = ['TL']
    message = 'Only Team Leads can access this resource.'


class IsProjectCoordinator(_RolePermission):
    """Grants access to Project Coordinator role (+ admins)."""
    allowed_roles = ['PC']
    message = 'Only Project Coordinators can access this resource.'


class IsEmployee(_RolePermission):
    """Grants access to Employee role (+ admins)."""
    allowed_roles = ['EMP']
    message = 'Only Employees can access this resource.'


class IsAnyMember(_RolePermission):
    """Grants access to any Member role: TL, PC, or EMP (+ admins)."""
    allowed_roles = ['TL', 'PC', 'EMP']
    message = 'You must be a registered member to access this resource.'
