"""
coreapp/views.py
-----------------
Template-based views for the PMS system:

1. Auth Views  – Login / Logout / Dashboard
2. Admin Views – AdminDashboardView (superuser only)
3. Member CRUD – List, Create, Update, Delete
4. Task CRUD   – List, Create, Update, Delete
"""
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Project, Member, Task
from .mixins import AdminRequiredMixin
from .forms import MemberCreateForm, MemberUpdateForm, TaskForm, ProjectForm


# ═══════════════════════════════════════════════════════════════════════════
#  Auth Views – Login / Logout / Dashboard
# ═══════════════════════════════════════════════════════════════════════════

class IndexView(View):
    """Public landing page with a Login button."""
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('admin-dashboard')
            return redirect('dashboard')
        return render(request, 'coreapp/index.html')


class MemberLoginView(View):
    """Custom login page for Members (TL, Employee, Project Coordinator)."""
    template_name = 'coreapp/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('admin-dashboard')
            return redirect('dashboard')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Superuser → custom admin dashboard
            if user.is_superuser:
                return redirect('admin-dashboard')
            # Member → role-based dashboard
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, self.template_name, {'username': username})


class MemberLogoutView(View):
    """Logs the user out and redirects to the login page."""
    def get(self, request):
        logout(request)
        return redirect('member-login')


class DashboardView(LoginRequiredMixin, View):
    """
    Role-aware dashboard.
    Reads the member's role and passes context to the unified dashboard template.
    Superusers who land here are redirected to admin.
    """
    login_url = 'member-login'

    def get(self, request):
        if request.user.is_superuser:
            return redirect('/admin/')
        try:
            member = request.user.member
        except Member.DoesNotExist:
            logout(request)
            messages.error(request, 'No member profile found for your account.')
            return redirect('member-login')

        # Role-specific context
        context = {'member': member}

        if member.is_team_lead:
            # TL sees all tasks in their project
            context['tasks'] = Task.objects.filter(
                project=member.project
            ).select_related('assigned_to__user') if member.project else Task.objects.none()
            context['team_members'] = Member.objects.filter(
                project=member.project
            ).select_related('user').exclude(pk=member.pk)

        elif member.is_project_coordinator:
            context['projects'] = Project.objects.all()
            context['total_members'] = Member.objects.filter(project=member.project).count()
            context['tasks'] = Task.objects.filter(
                project=member.project
            ).select_related('assigned_to__user') if member.project else Task.objects.none()

        else:  # Employee
            # Employee sees only their own tasks
            context['tasks'] = Task.objects.filter(
                assigned_to=member
            ).select_related('project')

        return render(request, 'coreapp/dashboard.html', context)


class AdminDashboardView(LoginRequiredMixin, View):
    """
    Custom admin dashboard – superuser only.
    Shows stats + full CRUD links for Members, Projects, and Tasks.
    """
    login_url = 'member-login'

    def get(self, request):
        if not request.user.is_superuser:
            return redirect('dashboard')

        context = {
            'total_members':  Member.objects.count(),
            'total_projects': Project.objects.count(),
            'total_tasks':    Task.objects.count(),
            'pending_tasks':  Task.objects.filter(status='pending').count(),
            'done_tasks':     Task.objects.filter(status='completed').count(),
            'recent_members': Member.objects.select_related('user', 'project').order_by('-created_at')[:5],
            'recent_tasks':   Task.objects.select_related('assigned_to__user', 'project').order_by('-created_at')[:5],
            'projects':       Project.objects.all(),
        }
        return render(request, 'coreapp/admin_dashboard.html', context)


# ═══════════════════════════════════════════════════════════════════════════
#  Member CRUD – Template Views
# ═══════════════════════════════════════════════════════════════════════════

class MemberListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Member
    template_name = 'coreapp/member_list.html'
    context_object_name = 'members'
    queryset = Member.objects.select_related('user', 'project').all()


class MemberCreateView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = 'coreapp/member_form.html'

    def get(self, request):
        form = MemberCreateForm()
        return render(request, self.template_name, {'form': form, 'title': 'Add Member'})

    def post(self, request):
        form = MemberCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('member-list')
        return render(request, self.template_name, {'form': form, 'title': 'Add Member'})


class MemberUpdateView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = 'coreapp/member_form.html'

    def get(self, request, pk):
        member = get_object_or_404(Member, pk=pk)
        form = MemberUpdateForm(member=member)
        return render(request, self.template_name, {'form': form, 'title': 'Edit Member', 'member': member})

    def post(self, request, pk):
        member = get_object_or_404(Member, pk=pk)
        form = MemberUpdateForm(request.POST, member=member)
        if form.is_valid():
            form.save(member)
            return redirect('member-list')
        return render(request, self.template_name, {'form': form, 'title': 'Edit Member', 'member': member})


class MemberDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Member
    template_name = 'coreapp/member_confirm_delete.html'
    success_url = reverse_lazy('member-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Delete Member'
        return ctx


# ═══════════════════════════════════════════════════════════════════════════
#  Task CRUD – Template Views
# ═══════════════════════════════════════════════════════════════════════════

class TaskListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Task
    template_name = 'coreapp/task_list.html'
    context_object_name = 'tasks'
    queryset = Task.objects.select_related('assigned_to__user', 'project').all()


class TaskCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'coreapp/task_form.html'
    success_url = reverse_lazy('task-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add Task'
        return ctx


class TaskUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'coreapp/task_form.html'
    success_url = reverse_lazy('task-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Task'
        return ctx


class TaskDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Task
    template_name = 'coreapp/task_confirm_delete.html'
    success_url = reverse_lazy('task-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Delete Task'
        return ctx


# ═══════════════════════════════════════════════════════════════════════════
#  Project CRUD – Template Views
# ═══════════════════════════════════════════════════════════════════════════

class ProjectListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Project
    template_name = 'coreapp/project_list.html'
    context_object_name = 'projects'
    queryset = Project.objects.all()


class ProjectCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'coreapp/project_form.html'
    success_url = reverse_lazy('project-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add Project'
        return ctx


class ProjectUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'coreapp/project_form.html'
    success_url = reverse_lazy('project-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Project'
        return ctx


class ProjectDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Project
    template_name = 'coreapp/project_confirm_delete.html'
    success_url = reverse_lazy('project-list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Delete Project'
        return ctx
