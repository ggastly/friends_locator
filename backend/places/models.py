from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser as User


class Place(models.Model):
    """Модель места на карте."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name=_("Пользователь"),
        help_text=_("Укажите пользователя"),
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Название места"),
        help_text=_("Введите название"),
    )
    latitude = models.FloatField(
        verbose_name=_("Широта"),
        help_text=_("Укажите широту"),
        validators=(MinValueValidator(-90.1), MaxValueValidator(90.1)),
    )
    longitude = models.FloatField(
        verbose_name=_("Долгота"),
        help_text=_("Укажите долготу"),
        validators=(MinValueValidator(-180.1), MaxValueValidator(90.1)),
    )

    class Meta:
        verbose_name = _("Место")
        verbose_name_plural = _("Места")
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("user", "name"), name="user_place"
            ),
        )

    def __str__(self):
        return self.name


class SharedPlaces(models.Model):
    """Модель шейринга местами между пользователями."""

    sharing_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sharing",
        verbose_name=_("Пользователь"),
        help_text=_("Укажите пользователя"),
    )
    sharing_to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sharing_to",
        verbose_name=_("Пользователь"),
        help_text=_("Укажите пользователя"),
    )
    sharing_place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="shared_place",
        verbose_name=_("Место"),
        help_text=_("Введите место"),
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("sharing_user", "sharing_to_user", "sharing_place"),
                name="sharing-place",
            ),
        )

    def __str__(self):
        return (
            f"{self.sharing_user} {self.sharing_to_user} {self.sharing_place}"
        )
