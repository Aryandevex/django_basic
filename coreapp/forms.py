"""
coreapp/forms.py
-----------------
Django forms for admin-facing CRUD views.

MemberCreateForm  – creates a new User + Member
MemberUpdateForm  – updates existing User credentials and Member fields
TaskForm          – create/update a Task
ProjectForm       – create/update a Project
"""
from django import forms
from django.contrib.auth.models import User
from .models import Member, Task, Project


# ── Member Forms ────────────────────────────────────────────────────────────

class MemberCreateForm(forms.Form):
    """Handles creating a new User and Member in one go."""
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    project  = forms.ModelChoiceField(
        queryset=Project.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=Member.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(username=data['username'], password=data['password'])
        member = Member.objects.create(
            user=user,
            project=data.get('project'),
            role=data['role'],
            phone=data.get('phone', ''),
        )
        return member


class MemberUpdateForm(forms.Form):
    """Allows admin to update Member credentials and assignment."""
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current'}),
        help_text='Leave blank to keep the existing password.'
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=Member.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, member=None, **kwargs):
        super().__init__(*args, **kwargs)
        if member:
            self.fields['username'].initial = member.user.username
            self.fields['project'].initial  = member.project
            self.fields['role'].initial     = member.role
            self.fields['phone'].initial    = member.phone

    def clean_username(self):
        username = self.cleaned_data['username']
        return username

    def save(self, member):
        data = self.cleaned_data
        member.user.username = data['username']
        if data.get('password'):
            member.user.set_password(data['password'])
        member.user.save()
        member.project = data.get('project')
        member.role    = data['role']
        member.phone   = data.get('phone', '')
        member.save()
        return member


# ── Task Form ───────────────────────────────────────────────────────────────

class TaskForm(forms.ModelForm):
    """Standard ModelForm for creating and updating Tasks."""

    class Meta:
        model  = Task
        fields = ['title', 'description', 'assigned_to', 'project', 'status', 'due_date']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'project':     forms.Select(attrs={'class': 'form-control'}),
            'status':      forms.Select(attrs={'class': 'form-control'}),
            'due_date':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


# ── Project Form ─────────────────────────────────────────────────────────────

class ProjectForm(forms.ModelForm):
    """Standard ModelForm for creating and updating Projects."""

    class Meta:
        model  = Project
        fields = ['name', 'description']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
