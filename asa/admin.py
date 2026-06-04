from django.contrib import admin
from .models import CouncilMember, Department, UserProfile, Member, Choir, ChoirMember, ChoirLeader, BaptismClass

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'gender', 'phone_number', 'registration_date']
    list_filter = ['gender']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']

@admin.register(CouncilMember)
class CouncilMemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'position']
    search_fields = ['first_name', 'last_name', 'position', 'email', 'phone_number']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'leader', 'registration_date']
    list_filter = ['name']
    search_fields = ['leader__first_name', 'leader__last_name']

@admin.register(Choir)
class ChoirAdmin(admin.ModelAdmin):
    list_display = ['name', 'registration_date']
    search_fields = ['name', 'description']

@admin.register(ChoirMember)
class ChoirMemberAdmin(admin.ModelAdmin):
    list_display = ['member', 'choir', 'role', 'join_date']
    list_filter = ['choir', 'role']
    search_fields = ['member__first_name', 'member__last_name', 'choir__name']

@admin.register(ChoirLeader)
class ChoirLeaderAdmin(admin.ModelAdmin):
    list_display = ['member', 'choir', 'position', 'is_active']
    list_filter = ['choir', 'is_active']
    search_fields = ['member__first_name', 'member__last_name', 'choir__name', 'position']

@admin.register(BaptismClass)
class BaptismClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'instructor', 'start_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'instructor__first_name', 'instructor__last_name']
