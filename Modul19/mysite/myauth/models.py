from django.db import models
from django.contrib.auth.models import User


def profile_preview_directory_path(instance: "Profile", filename: str) -> str:
    return "profiles/profile_{pk}/avatar/{filename}".format(
        pk=instance.user,
        filename=filename,
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_preview_directory_path)
