"""
coreapp/serializers.py
-----------------------
Serializer-based architecture using Django REST Framework.

- ProjectSerializer: standard CRUD for Project model
- MemberSerializer: creates/updates both User and Member objects
  - create() → calls User.objects.create_user() for secure password hashing
  - update() → syncs username, password, project assignment
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Member


class ProjectSerializer(serializers.ModelSerializer):
    """Handles full CRUD for the Project model."""

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class MemberSerializer(serializers.ModelSerializer):
    """
    Handles full CRUD for Member + associated User.

    Extra write-only fields expose username/password at the API level
    without leaking them in responses.
    """
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    # Display project name alongside the FK id
    project_name = serializers.CharField(source='project.name', read_only=True)
    # Human-readable role label (e.g. "Team Lead" instead of "TL")
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = Member
        fields = [
            'id',
            'username',
            'password',
            'project',
            'project_name',
            'role',
            'role_display',
            'phone',
            'created_at',
        ]
        read_only_fields = ['id', 'project_name', 'role_display', 'created_at']

    def create(self, validated_data):
        """
        Step 1 – Extract auth fields.
        Step 2 – Create User with hashed password via create_user().
        Step 3 – Create Member linked to that User.
        """
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        # Secure user creation – password is automatically hashed
        user = User.objects.create_user(username=username, password=password)

        member = Member.objects.create(user=user, **validated_data)
        return member

    def update(self, instance, validated_data):
        """
        Allows admin to update username, password, and project assignment.
        Password is re-hashed securely via set_password().
        """
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)

        # Update User credentials if provided
        if username:
            instance.user.username = username
        if password:
            instance.user.set_password(password)
        instance.user.save()

        # Update Member-level fields
        instance.project = validated_data.get('project', instance.project)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.save()

        return instance
