from django.urls import path
from .views import (
    TaskListCreateView, TaskDetailView, mark_task_completed,
    mark_task_pending, task_statistics, OverdueTasksView
)

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/complete/', mark_task_completed, name='task-complete'),
    path('<int:pk>/pending/', mark_task_pending, name='task-pending'),
    path('statistics/', task_statistics, name='task-statistics'),
    path('overdue/', OverdueTasksView.as_view(), name='overdue-tasks'),
]
