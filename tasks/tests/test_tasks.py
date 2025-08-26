import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()

@pytest.mark.django_db
class TestTaskModel:
    def test_task_creation(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            user=user
        )

        assert task.title == 'Test Task'
        assert task.status == 'pending'
        assert task.priority == 'medium'
        assert task.user == user

    def test_task_str_representation(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        task = Task.objects.create(
            title='Test Task',
            user=user,
            status='completed'
        )

        assert str(task) == 'Test Task - Completed'

    def test_task_is_overdue(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        # Past due date
        past_date = timezone.now() - timezone.timedelta(days=1)
        overdue_task = Task.objects.create(
            title='Overdue Task',
            user=user,
            due_date=past_date
        )

        assert overdue_task.is_overdue is True

        # Future due date
        future_date = timezone.now() + timezone.timedelta(days=1)
        future_task = Task.objects.create(
            title='Future Task',
            user=user,
            due_date=future_date
        )

        assert future_task.is_overdue is False


@pytest.mark.django_db
class TestTaskAPI:
    def test_create_task(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('task-list-create')
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'priority': 'high'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.filter(title='New Task').exists()

    def test_list_user_tasks(self):
        user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )

        # Create tasks for both users
        Task.objects.create(title='User1 Task', user=user1)
        Task.objects.create(title='User2 Task', user=user2)

        client = APIClient()
        client.force_authenticate(user=user1)

        url = reverse('task-list-create')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'User1 Task'

    def test_update_task(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        task = Task.objects.create(
            title='Original Title',
            user=user
        )

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {
            'title': 'Updated Title',
            'status': 'completed'
        }

        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Updated Title'
        assert task.status == 'completed'

    def test_delete_task(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        task = Task.objects.create(
            title='Task to Delete',
            user=user
        )

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_mark_task_completed(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        task = Task.objects.create(
            title='Task to Complete',
            user=user
        )

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('task-complete', kwargs={'pk': task.pk})
        response = client.patch(url)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == 'completed'

    def test_task_statistics(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        # Create various tasks
        Task.objects.create(title='Pending Task', user=user, status='pending')
        Task.objects.create(title='Completed Task', user=user, status='completed')
        Task.objects.create(title='High Priority Task', user=user, priority='high')

        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse('task-statistics')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_tasks'] == 3
        assert response.data['completed_tasks'] == 1
        assert response.data['pending_tasks'] == 2
        assert response.data['high_priority_tasks'] == 1
