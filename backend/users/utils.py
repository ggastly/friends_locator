import os

from django.conf import settings


def media_folder_cleaner():
    """Удаление пустых папок."""

    media_path = settings.MEDIA_ROOT / "uploads"

    for dirpath, _, _ in os.walk(media_path, topdown=False):
        if dirpath == media_path:
            break
        try:
            os.rmdir(dirpath)
        except OSError:
            pass
