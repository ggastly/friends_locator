from rest_framework.viewsets import ReadOnlyModelViewSet

from users.models import Tag
from .serializers import TagSerializer


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели Тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
