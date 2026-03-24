"""
coreapp/mixins.py
-----------------
Reusable permission mixins for class-based views (CBVs).

Role Hierarchy:
    Admin (superuser) → full system access
    Team Lead (TL)    → can manage their team's tasks/members
    Project Coordinator (PC) → can manage project-level details
    Employee (EMP)    → view-only dashboard access

NOTE:
- For Django CBVs (TemplateView, ListView, etc.) → use these mixins.
- For DRF ViewSets (API) → use permission_classes instead (see permissions.py).

Following the DRY principle: write once, reuse everywhere.
"""
from django.contrib.auth.mixins import UserPassesTestMixin


# ── Admin ──────────────────────────────────────────────────────────────────

class AdminRequiredMixin(UserPassesTestMixin):
    """Restricts view to Django superusers only."""
    def test_func(self):
        return self.request.user.is_superuser


# ── Role-Based Mixins ──────────────────────────────────────────────────────

class _MemberRoleTestMixin(UserPassesTestMixin):
    """
    Base mixin that checks the authenticated user's Member role.
    Subclasses override `allowed_roles` with a list of role codes.
    """
    allowed_roles = []   # override in subclass, e.g. ['TL', 'PC']

    def test_func(self):
        user = self.request.user
        # Superuser always passes
        if user.is_superuser:
            return True
        # Must be an authenticated member with one of the allowed roles
        try:
            return user.member.role in self.allowed_roles
        except AttributeError:
            return False


class TeamLeadMixin(_MemberRoleTestMixin):
    """
    Allows Team Leads (and admins) to access the view.

    Usage:
        class TeamDashboard(TeamLeadMixin, TemplateView):
            template_name = 'tl_dashboard.html'
    """
    allowed_roles = ['TL']


class ProjectCoordinatorMixin(_MemberRoleTestMixin):
    """
    Allows Project Coordinators (and admins) to access the view.

    Usage:
        class ProjectView(ProjectCoordinatorMixin, TemplateView):
            template_name = 'pc_dashboard.html'
    """
    allowed_roles = ['PC']


class EmployeeMixin(_MemberRoleTestMixin):
    """
    Allows Employees (and admins) to access the view.

    Usage:
        class EmployeeDashboard(EmployeeMixin, TemplateView):
            template_name = 'emp_dashboard.html'
    """
    allowed_roles = ['EMP']


class AnyMemberMixin(_MemberRoleTestMixin):
    """
    Allows any member regardless of role (TL, PC, or EMP) plus admins.
    Use for views accessible to all logged-in members.
    """
    allowed_roles = ['TL', 'PC', 'EMP']
