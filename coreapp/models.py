from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    """Stores project information managed by the admin."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Member(models.Model):
    """
    Represents an authenticated member in the system.
    - OneToOne with Django User (handles login credentials)
    - ForeignKey to Project (business relationship)
    - Role determines dashboard access level
    """

    # ── Role Choices ──────────────────────────────────────────
    TEAM_LEAD          = 'TL'
    EMPLOYEE           = 'EMP'
    PROJECT_COORDINATOR = 'PC'

    ROLE_CHOICES = [
        (TEAM_LEAD,          'Team Lead'),
        (EMPLOYEE,           'Employee'),
        (PROJECT_COORDINATOR, 'Project Coordinator'),
    ]
    # ──────────────────────────────────────────────────────────

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member')
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    role = models.CharField(
        max_length=3,
        choices=ROLE_CHOICES,
        default=EMPLOYEE,
    )
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ── Role helper properties ─────────────────────────────────
    @property
    def is_team_lead(self):
        return self.role == self.TEAM_LEAD

    @property
    def is_employee(self):
        return self.role == self.EMPLOYEE

    @property
    def is_project_coordinator(self):
        return self.role == self.PROJECT_COORDINATOR
    # ──────────────────────────────────────────────────────────

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    class Meta:
        ordering = ['-created_at']


class Task(models.Model):
    """Represents a task assigned to a member within a project."""

    STATUS_PENDING     = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED   = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING,     'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED,   'Completed'),
    ]

    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks'
    )
    project     = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks'
    )
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    due_date    = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
