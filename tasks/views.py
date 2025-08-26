from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Task
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, TaskListSerializer
)
from .permissions import IsTaskOwner, IsAuthenticatedAndOwner


class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedAndOwner]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskUpdateSerializer
        return TaskSerializer


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_task_completed(request, pk):
    try:
        task = Task.objects.get(pk=pk, user=request.user)
        task.mark_completed()
        serializer = TaskSerializer(task)
        return Response({
            'message': 'Task marked as completed',
            'task': serializer.data
        }, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({
            'error': 'Task not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_task_pending(request, pk):
    try:
        task = Task.objects.get(pk=pk, user=request.user)
        task.mark_pending()
        serializer = TaskSerializer(task)
        return Response({
            'message': 'Task marked as pending',
            'task': serializer.data
        }, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({
            'error': 'Task not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_statistics(request):
    user_tasks = Task.objects.filter(user=request.user)

    stats = {
        'total_tasks': user_tasks.count(),
        'completed_tasks': user_tasks.filter(status='completed').count(),
        'pending_tasks': user_tasks.filter(status='pending').count(),
        'in_progress_tasks': user_tasks.filter(status='in_progress').count(),
        'overdue_tasks': sum(1 for task in user_tasks if task.is_overdue),
        'high_priority_tasks': user_tasks.filter(priority='high').count(),
        'urgent_priority_tasks': user_tasks.filter(priority='urgent').count(),
    }

    return Response(stats, status=status.HTTP_200_OK)


class OverdueTasksView(generics.ListAPIView):
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_tasks = Task.objects.filter(user=self.request.user)
        return [task for task in user_tasks if task.is_overdue]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(queryset),
            'results': serializer.data
        })
