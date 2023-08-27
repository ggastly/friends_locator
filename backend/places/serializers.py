from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Place, SharedPlaces


class PlacesSerializer(serializers.ModelSerializer):
    """Сериализатор для мест"""

    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Place
        fields = ("user", "name", "latitude", "longitude")


class SharingSerializer(serializers.ModelSerializer):
    """Сериализатор для мест"""

    sharing_user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    def validate(self, attrs):
        if SharedPlaces.objects.filter(
            sharing_place=attrs["sharing_place"],
            sharing_to_user=attrs["sharing_to_user"],
            sharing_user=self.context["request"].user,
        ).exists():
            raise ValidationError(
                "Это место уже шарится данному пользователю."
            )
        if attrs["sharing_to_user"] == self.context["request"].user:
            raise ValidationError("Нельзя шарить самому себе.")
        return attrs

    class Meta:
        model = SharedPlaces
        fields = ("sharing_user", "sharing_to_user", "sharing_place")
