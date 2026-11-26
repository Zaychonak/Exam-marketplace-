from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsOwnerReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'market'):
            return obj.market.user == request.user

        return obj.user == request.user
