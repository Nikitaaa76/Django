from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(pk=3)
        group, created = Group.objects.get_or_create(
            name="profile_management",
        )
        permission_profile = Permission.objects.get(
            codename="view_profile",
        )
        permission_logentry = Permission.objects.get(
            codename="view_logentry",
        )
        # adding a permission to a group
        group.permissions.add(permission_profile)

        # joining a user to a group
        user.groups.add(group)

        # link a user to permission
        user.user_permissions.add(permission_logentry)

        group.save()
        user.save()
