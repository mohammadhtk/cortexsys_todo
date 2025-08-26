import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    def test_user_registration_success(self):
        client = APIClient()
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert User.objects.filter(email='test@example.com').exists()

    def test_user_registration_password_mismatch(self):
        client = APIClient()
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(email='test@example.com').exists()


@pytest.mark.django_db
class TestUserLogin:
    def test_user_login_success(self):
        # Create a user
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        client = APIClient()
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        client = APIClient()
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserProfile:
    def test_get_user_profile(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('profile')

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@example.com'
        assert response.data['username'] == 'testuser'
