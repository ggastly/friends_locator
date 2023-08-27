import base64
from re import match

from django.conf import settings
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (CurrentUserDefault, HiddenField,
                                        ImageField, ModelSerializer,
                                        SerializerMethodField, ValidationError)

from .models import CustomUser as User
from .models import FriendsRelationship


class Base64ImageField(ImageField):
    """Класс для добавления добавления аватара при создании пользователя."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):
    """Кастомный сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "gender",
        )
        write_only_fields = ("password",)

    def validate_first_name(self, value):
        if not match(settings.NAME_REGEX_PATTERN, value):
            raise ValidationError("Некорректное имя пользователя.")
        return value

    def validate_last_name(self, value):
        if not match(settings.NAME_REGEX_PATTERN, value):
            raise ValidationError("Некорректная фамилия пользователя.")
        return value


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор для работы с пользователем."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "longitude",
            "latitude",
            "status",
            "userpic",
        )


class UserpicSerializer(ModelSerializer):
    """Кастомный сериализатор для работы с аватаром пользователя."""

    user = HiddenField(default=CurrentUserDefault())
    userpic = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "user",
            "userpic",
        )

    read_only_fields = ("user",)


class FriendsRelationshipSerializer(ModelSerializer):
    """Кастомный сериализатор для работы с дружескими связями."""
    class Meta:
        model = FriendsRelationship
        fields = (
            "current_user",
            "friend",
            "friend_category",
        )


class FriendSerializer(ModelSerializer):
    """Кастомный сериализатор для работы с друзьями."""
    friend_category = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "longitude",
            "latitude",
            "friend_category",
        )
        read_only_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "longitude",
            "latitude",
            "friend_category",
        )

    def get_friend_category(self, data):
        return data.friend_category


class CoordinateSerializer(ModelSerializer):
    """Кастомный сериализатор для работы с координатами."""

    class Meta:
        model = User
        fields = (
            "longitude",
            "latitude",
        )

    def validate(self, data):
        if "longitude" not in data or "latitude" not in data:
            raise ValidationError(
                "Требуется передавать оба параметра широты и долготы."
            )
        return data


class UserStatusSerializer(ModelSerializer):
    """Сериализатор для обновления статуса пользователя."""

    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = User
        fields = (
            "user",
            "status",
        )
        read_only_fields = ("user",)
