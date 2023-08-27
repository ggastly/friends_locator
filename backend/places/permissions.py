from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """Только автор может просматривать свои места."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.id == int(
            request.parser_context["kwargs"]["user_id"]
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user == request.user
