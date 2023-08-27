from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from users.models import CustomUser
from users.utils import media_folder_cleaner


@receiver(post_delete, sender=CustomUser)
def post_delete_image(sender, instance, *args, **kwargs):
    """Сигнал на удаление картинки."""

    try:
        instance.userpic.delete(save=False)
        media_folder_cleaner()
    except Exception:
        pass


@receiver(pre_save, sender=CustomUser)
def pre_save_image(sender, instance, *args, **kwargs):
    """Сигнал на удаление старой картинки при обновлении картинки."""

    try:
        old_img = instance.__class__.objects.get(id=instance.id).userpic.path
        try:
            new_img = instance.userpic.path
        except Exception:
            new_img = None
        if new_img != old_img:
            import os

            if os.path.exists(old_img):
                os.remove(old_img)
                media_folder_cleaner()
    except Exception:
        pass


post_delete.connect(post_delete_image, sender=CustomUser)
pre_save.connect(pre_save_image, sender=CustomUser)
