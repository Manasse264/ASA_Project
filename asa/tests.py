from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Member, Choir, ChoirMember, BaptismClass, UserProfile

class ASAFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.secretary_user = User.objects.create_user(username='secretary', password='password')
        # UserProfile is created via signal
        self.secretary_profile = self.secretary_user.profile
        self.secretary_profile.role = 'SECRETARY'
        self.secretary_profile.save()
        
        self.choir = Choir.objects.create(name='Heavenly Voices')

    def test_choir_member_creation(self):
        """Test that adding a choir member creates a new member record."""
        self.client.login(username='secretary', password='password')
        response = self.client.post(reverse('choir_member_add', args=[self.choir.pk]), {
            'first_name': 'New',
            'last_name': 'Singer',
            'gender': 'F',
            'date_of_birth': '2000-01-01',
            'role': 'Alto'
        })
        self.assertEqual(response.status_code, 302)
        member = Member.objects.get(first_name='New', last_name='Singer')
        self.assertTrue(ChoirMember.objects.filter(choir=self.choir, member=member, role='Alto').exists())

    def test_baptism_candidate_registration(self):
        """Test registering a new baptism candidate."""
        self.client.login(username='secretary', password='password')
        response = self.client.post(reverse('candidate_create'), {
            'first_name': 'Candidate',
            'last_name': 'One',
            'gender': 'M',
            'date_of_birth': '1995-05-05'
        })
        self.assertEqual(response.status_code, 302)
        candidate = Member.objects.get(first_name='Candidate', last_name='One')
        self.assertEqual(candidate.status, 'CANDIDATE')

    def test_user_self_registration(self):
        """Test that a user can self-register with a specific role."""
        response = self.client.post(reverse('register'), {
            'username': 'new_treasurer',
            'email': 'treasurer@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'TREASURER'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_treasurer').exists())
        user = User.objects.get(username='new_treasurer')
        self.assertEqual(user.profile.role, 'TREASURER')
