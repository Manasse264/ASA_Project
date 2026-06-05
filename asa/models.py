from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ELDER', 'First Church Elder'),
        ('SECRETARY', 'Church Secretary'),
        ('TREASURER', 'Church Treasurer'),
        ('SS_LEADER', 'Sabbath School Leader'),
        ('CHOIR_LEADER', 'Choir Leader'),
        ('DEPT_LEADER', 'Department Leader'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DEPT_LEADER')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)
    instance.profile.save()

class Family(models.Model):
    name = models.CharField(max_length=100, unique=True)
    head_of_family = models.ForeignKey('Member', on_delete=models.SET_NULL, blank=True, null=True, related_name='headed_family')
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Member(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    STATUS_CHOICES = [
        ('CANDIDATE', 'Baptism Candidate'),
        ('MEMBER', 'Full Member'),
        ('INACTIVE', 'Inactive'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_baptized = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='MEMBER')
    baptism_date = models.DateField(blank=True, null=True)
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, blank=True, null=True, related_name='members')
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class SabbathSchoolSession(models.Model):
    date = models.DateField(unique=True)
    recorder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_submitted = models.BooleanField(default=False)
    submission_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sabbath School - {self.date}"

class MemberAttendance(models.Model):
    session = models.ForeignKey(SabbathSchoolSession, on_delete=models.CASCADE, related_name='attendance_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendance_history')
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'member')

    def __str__(self):
        return f"{self.member.full_name} - {self.session.date} - {'Present' if self.is_present else 'Absent'}"

class BaptismClass(models.Model):
    name = models.CharField(max_length=100)
    instructor = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='instructed_classes')
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    candidates = models.ManyToManyField(Member, related_name='baptism_classes', limit_choices_to={'status': 'CANDIDATE'})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Baptism Classes"

class CouncilMember(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Department(models.Model):
    DEPARTMENT_CHOICES = [
        ('WELFARE', 'Welfare'),
        ('TEMPERANCE_FAMILY', 'Temperance and Family'),
        ('JA', 'J.A'),
        ('MIFEM', 'MIFEM'),
        ('CHILDREN', 'Children Department'),
    ]

    name = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES, unique=True)
    leader = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='led_departments')
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_name_display()

class Choir(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ChoirMember(models.Model):
    choir = models.ForeignKey(Choir, on_delete=models.CASCADE, related_name='members')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True, null=True) # e.g. Soprano, Alto, Tenor, Bass
    join_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('choir', 'member')

    def __str__(self):
        return f"{self.member.full_name} in {self.choir.name}"

class ChoirLeader(models.Model):
    choir = models.ForeignKey(Choir, on_delete=models.CASCADE, related_name='leaders')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    position = models.CharField(max_length=100) # e.g. Director, Assistant Director
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.member.full_name} - {self.position} ({self.choir.name})"
