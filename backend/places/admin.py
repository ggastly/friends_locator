from django.contrib import admin

from .models import Place


@admin.register(Place)
class CustomUserAdmin(admin.ModelAdmin):
    """Админка для юзеров."""

    list_display = (
        "pk",
        "user",
        "name",
        "latitude",
        "longitude",
    )

    def has_add_permission(self, request):
        return False
