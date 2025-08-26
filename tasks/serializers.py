from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'user', 'created_at', 'updated_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value.strip()

    def validate(self, attrs):
        # Check if due_date is in the future for new tasks
        if self.instance is None and attrs.get('due_date'):
            from django.utils import timezone
            if attrs['due_date'] < timezone.now():
                raise serializers.ValidationError({
                    'due_date': 'Due date cannot be in the past'
                })
        return attrs


class TaskCreateSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        fields = [
            'title', 'description', 'status', 'priority', 'due_date'
        ]


class TaskUpdateSerializer(TaskSerializer):
    class Meta(TaskSerializer.Meta):
        fields = [
            'title', 'description', 'status', 'priority', 'due_date'
        ]


class TaskListSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority', 'due_date',
            'created_at', 'is_overdue'
        ]
