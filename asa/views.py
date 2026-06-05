import datetime
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.db.models import Q
from .models import CouncilMember, Department, Member, Choir, ChoirMember, ChoirLeader, BaptismClass
from .forms import CouncilMemberForm, DepartmentForm, MemberForm, ChoirForm, ChoirMemberForm, ChoirLeaderForm, ChoirMemberCreateForm, BaptismCandidateForm, BaptismClassForm, UserRegistrationForm

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            profile = user.profile
            profile.role = form.cleaned_data['role']
            profile.save()
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'asa/register.html', {'form': form})

SECRETARY_USERNAMES = {'secretary', 'churchsecretary', 'church_secretary'}

def is_secretary(user):
    if not user.is_authenticated:
        return False
    # Use hasattr and getattr safely
    profile = getattr(user, 'profile', None)
    profile_role = getattr(profile, 'role', None) if profile else None
    
    return (
        profile_role == 'SECRETARY'
        or user.groups.filter(name__iexact='Church Secretary').exists()
        or user.username.lower().replace(' ', '_') in SECRETARY_USERNAMES
    )

def is_elder(user):
    if not user.is_authenticated:
        return False
    profile = getattr(user, 'profile', None)
    profile_role = getattr(profile, 'role', None) if profile else None
    return profile_role == 'ELDER' or user.groups.filter(name__iexact='First Church Elder').exists()

def base_context(user):
    is_secretary_user = is_secretary(user)
    return {
        'is_secretary_user': is_secretary_user,
        'can_view_members': is_secretary_user or is_elder(user),
    }

class RoleBasedLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        if is_secretary(self.request.user):
            return '/'
        return super().get_success_url()

def csrf_failure(request, reason=''):
    if request.path == '/accounts/login/':
        return redirect('login')
    return HttpResponseForbidden('CSRF verification failed. Request aborted.')

def role_required(allowed_roles):
    def check_role(user):
        if not user.is_authenticated:
            return False
        if 'SECRETARY' in allowed_roles and is_secretary(user):
            return True
        if 'ELDER' in allowed_roles and is_elder(user):
            return True
        return getattr(getattr(user, 'profile', None), 'role', None) in allowed_roles
    return user_passes_test(check_role)

def index(request):
    context = base_context(request.user)
    if context['is_secretary_user']:
        context['member_count'] = Member.objects.filter(status='MEMBER').count()
        context['department_count'] = Department.objects.count()
    return render(request, 'asa/index.html', context)

@login_required
@role_required(['SECRETARY', 'ELDER'])
def member_list(request):
    query = request.GET.get('q')
    members = Member.objects.filter(status='MEMBER')
    
    if query:
        members = members.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
        )
    
    members = members.order_by('last_name', 'first_name')
    
    context = {
        'members': members,
        'query': query,
        **base_context(request.user),
    }
    if context['is_secretary_user']:
        context['member_count'] = Member.objects.filter(status='MEMBER').count()
    return render(request, 'asa/member_list.html', context)

@login_required
@role_required(['SECRETARY', 'ELDER'])
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, 'asa/member_detail.html', {'member': member, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm()
    return render(request, 'asa/member_form.html', {'form': form, 'title': 'Add Member', **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('member_detail', pk=pk)
    else:
        form = MemberForm(instance=member)
    return render(request, 'asa/member_form.html', {'form': form, 'title': 'Edit Member', 'member': member, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        return redirect('member_list')
    return render(request, 'asa/member_confirm_delete.html', {'member': member, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def council_member_list(request):
    query = request.GET.get('q')
    if query:
        council_members = CouncilMember.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(position__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )
    else:
        council_members = CouncilMember.objects.all().order_by('last_name', 'first_name')

    return render(request, 'asa/council_member_list.html', {
        'council_members': council_members,
        'query': query,
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def council_member_detail(request, pk):
    council_member = get_object_or_404(CouncilMember, pk=pk)
    return render(request, 'asa/council_member_detail.html', {
        'council_member': council_member,
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def council_member_create(request):
    if request.method == 'POST':
        form = CouncilMemberForm(request.POST)
        if form.is_valid():
            council_member = form.save()
            return redirect('council_member_detail', pk=council_member.pk)
    else:
        form = CouncilMemberForm()
    return render(request, 'asa/council_member_form.html', {
        'form': form,
        'title': 'Add Council Member',
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def council_member_update(request, pk):
    council_member = get_object_or_404(CouncilMember, pk=pk)
    if request.method == 'POST':
        form = CouncilMemberForm(request.POST, instance=council_member)
        if form.is_valid():
            form.save()
            return redirect('council_member_detail', pk=pk)
    else:
        form = CouncilMemberForm(instance=council_member)
    return render(request, 'asa/council_member_form.html', {
        'form': form,
        'title': 'Update Council Member',
        'council_member': council_member,
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def council_member_delete(request, pk):
    council_member = get_object_or_404(CouncilMember, pk=pk)
    if request.method == 'POST':
        council_member.delete()
        return redirect('council_member_list')
    return render(request, 'asa/council_member_confirm_delete.html', {
        'council_member': council_member,
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def department_list(request):
    query = request.GET.get('q')
    if query:
        departments = Department.objects.select_related('leader').filter(
            Q(name__icontains=query)
            | Q(leader__first_name__icontains=query)
            | Q(leader__last_name__icontains=query)
            | Q(leader__phone_number__icontains=query)
        )
    else:
        departments = Department.objects.select_related('leader').all().order_by('name')

    return render(request, 'asa/department_list.html', {
        'departments': departments,
        'query': query,
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    return render(request, 'asa/department_detail.html', {
        'department': department,
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            return redirect('department_detail', pk=department.pk)
    else:
        form = DepartmentForm()
    return render(request, 'asa/department_form.html', {
        'form': form,
        'title': 'Register Department',
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_detail', pk=pk)
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'asa/department_form.html', {
        'form': form,
        'title': 'Update Department',
        'department': department,
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('department_list')
    return render(request, 'asa/department_confirm_delete.html', {
        'department': department,
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def choir_list(request):
    query = request.GET.get('q')
    if query:
        choirs = Choir.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        choirs = Choir.objects.all().order_by('name')
    return render(request, 'asa/choir_list.html', {'choirs': choirs, 'query': query, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def choir_detail(request, pk):
    choir = get_object_or_404(Choir, pk=pk)
    members = choir.members.all().select_related('member')
    leaders = choir.leaders.all().select_related('member')
    return render(request, 'asa/choir_detail.html', {
        'choir': choir,
        'members': members,
        'leaders': leaders,
        **base_context(request.user)
    })

@login_required
@role_required(['SECRETARY'])
def choir_create(request):
    if request.method == 'POST':
        form = ChoirForm(request.POST)
        if form.is_valid():
            choir = form.save()
            return redirect('choir_detail', pk=choir.pk)
    else:
        form = ChoirForm()
    return render(request, 'asa/choir_form.html', {'form': form, 'title': 'Register Choir', **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def choir_update(request, pk):
    choir = get_object_or_404(Choir, pk=pk)
    if request.method == 'POST':
        form = ChoirForm(request.POST, instance=choir)
        if form.is_valid():
            form.save()
            return redirect('choir_detail', pk=pk)
    else:
        form = ChoirForm(instance=choir)
    return render(request, 'asa/choir_form.html', {'form': form, 'title': 'Update Choir', 'choir': choir, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def choir_delete(request, pk):
    choir = get_object_or_404(Choir, pk=pk)
    if request.method == 'POST':
        choir.delete()
        return redirect('choir_list')
    return render(request, 'asa/choir_confirm_delete.html', {'choir': choir, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def choir_member_add(request, choir_pk):
    choir = get_object_or_404(Choir, pk=choir_pk)
    if request.method == 'POST':
        form = ChoirMemberCreateForm(request.POST)
        if form.is_valid():
            member = form.save()
            ChoirMember.objects.create(
                choir=choir,
                member=member,
                role=form.cleaned_data.get('role')
            )
            return redirect('choir_detail', pk=choir_pk)
    else:
        form = ChoirMemberCreateForm()
    return render(request, 'asa/choir_member_form.html', {'form': form, 'choir': choir, 'title': f'Add Choir Member for {choir.name}', **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def choir_member_update(request, pk):
    choir_member = get_object_or_404(ChoirMember, pk=pk)
    if request.method == 'POST':
        form = ChoirMemberForm(request.POST, instance=choir_member)
        if form.is_valid():
            form.save()
            return redirect('choir_detail', pk=choir_member.choir.pk)
    else:
        form = ChoirMemberForm(instance=choir_member)
    return render(request, 'asa/choir_member_form.html', {'form': form, 'choir': choir_member.choir, 'title': 'Update Choir Member', **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def choir_member_delete(request, pk):
    choir_member = get_object_or_404(ChoirMember, pk=pk)
    choir_pk = choir_member.choir.pk
    if request.method == 'POST':
        choir_member.delete()
        return redirect('choir_detail', pk=choir_pk)
    return render(request, 'asa/choir_member_confirm_delete.html', {'choir_member': choir_member, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def choir_leader_add(request, choir_pk):
    choir = get_object_or_404(Choir, pk=choir_pk)
    if request.method == 'POST':
        form = ChoirLeaderForm(request.POST)
        if form.is_valid():
            choir_leader = form.save(commit=False)
            choir_leader.choir = choir
            choir_leader.save()
            return redirect('choir_detail', pk=choir_pk)
    else:
        form = ChoirLeaderForm()
    return render(request, 'asa/choir_leader_form.html', {'form': form, 'choir': choir, 'title': 'Add Choir Leader', **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def choir_leader_update(request, pk):
    choir_leader = get_object_or_404(ChoirLeader, pk=pk)
    if request.method == 'POST':
        form = ChoirLeaderForm(request.POST, instance=choir_leader)
        if form.is_valid():
            form.save()
            return redirect('choir_detail', pk=choir_leader.choir.pk)
    else:
        form = ChoirLeaderForm(instance=choir_leader)
    return render(request, 'asa/choir_leader_form.html', {'form': form, 'choir': choir_leader.choir, 'title': 'Update Choir Leader', **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def choir_leader_delete(request, pk):
    choir_leader = get_object_or_404(ChoirLeader, pk=pk)
    choir_pk = choir_leader.choir.pk
    if request.method == 'POST':
        choir_leader.delete()
        return redirect('choir_detail', pk=choir_pk)
    return render(request, 'asa/choir_leader_confirm_delete.html', {'choir_leader': choir_leader, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def candidate_list(request):
    query = request.GET.get('q')
    selected_year = request.GET.get('year')
    
    candidates = Member.objects.filter(status='CANDIDATE')
    
    if query:
        candidates = candidates.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
        )
    
    if selected_year and selected_year.isdigit():
        candidates = candidates.filter(registration_date__year=int(selected_year))
        
    candidates = candidates.order_by('last_name', 'first_name')
    
    # Get unique years from registration_date for all candidates
    years = list(Member.objects.filter(status='CANDIDATE').values_list('registration_date__year', flat=True).distinct().order_by('-registration_date__year'))
    current_year = datetime.date.today().year
    if current_year not in years:
        years.insert(0, current_year)
    
    return render(request, 'asa/candidate_list.html', {
        'candidates': candidates,
        'query': query,
        'years': years,
        'selected_year': selected_year,
        **base_context(request.user),
    })

@login_required
@role_required(['SECRETARY'])
def candidate_create(request):
    if request.method == 'POST':
        form = BaptismCandidateForm(request.POST)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.status = 'CANDIDATE'
            candidate.save()
            return redirect('candidate_list')
    else:
        form = BaptismCandidateForm()
    return render(request, 'asa/candidate_form.html', {'form': form, 'title': 'Register Candidate', **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def baptism_class_list(request):
    classes = BaptismClass.objects.all().order_by('-start_date')
    return render(request, 'asa/baptism_class_list.html', {'classes': classes, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def baptism_class_detail(request, pk):
    baptism_class = get_object_or_404(BaptismClass, pk=pk)
    return render(request, 'asa/baptism_class_detail.html', {'baptism_class': baptism_class, **base_context(request.user)})

@login_required
@role_required(['SECRETARY'])
def baptism_class_create(request):
    if request.method == 'POST':
        form = BaptismClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('baptism_class_list')
    else:
        form = BaptismClassForm()
    return render(request, 'asa/baptism_class_form.html', {'form': form, 'title': 'Create Baptism Class', **base_context(request.user)})
