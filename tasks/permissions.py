from rest_framework import permissions


class IsTaskOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the task.
        return obj.user == request.user


class IsAuthenticatedAndOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
