from rest_framework.serializers import ModelSerializer

from users.models import Tag


class TagSerializer(ModelSerializer):
    """Сериализатор для модели Тегов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
