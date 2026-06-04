from django import forms
from django.contrib.auth.models import User
from .models import CouncilMember, Department, Member, Choir, ChoirMember, ChoirLeader, BaptismClass, UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[
        ('TREASURER', 'Church Treasurer'),
        ('SS_LEADER', 'Sabbath School Leader'),
    ])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'phone_number', 'email', 'address', 'baptism_date', 'status']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'baptism_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class ChoirMemberCreateForm(forms.ModelForm):
    role = forms.CharField(max_length=50, required=False, label="Role")

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'phone_number', 'email', 'address']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class BaptismCandidateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'phone_number', 'email', 'address']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class BaptismClassForm(forms.ModelForm):
    class Meta:
        model = BaptismClass
        fields = ['name', 'instructor', 'start_date', 'is_active', 'candidates']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CouncilMemberForm(forms.ModelForm):
    class Meta:
        model = CouncilMember
        fields = [
            'first_name',
            'last_name',
            'position',
            'phone_number',
            'email',
            'responsibilities',
        ]
        widgets = {
            'responsibilities': forms.Textarea(attrs={'rows': 3}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'leader']

class ChoirForm(forms.ModelForm):
    class Meta:
        model = Choir
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ChoirMemberForm(forms.ModelForm):
    class Meta:
        model = ChoirMember
        fields = ['member', 'role']

class ChoirLeaderForm(forms.ModelForm):
    class Meta:
        model = ChoirLeader
        fields = ['member', 'position', 'is_active']
