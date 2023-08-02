from django.core.management import BaseCommand
from django.contrib.auth.models import User

from shopapp.models import Order


class Command(BaseCommand):
    """
    Creates orders
    """
    def handle(self, *args, **options):
        self.stdout.write("Create order")
        user = User.objects.get(username="admin")
        order = Order.objects.get_or_create(
            delivery_address="Ul Veteranov d 14",
            promocode="SALE123",
            user=user,
        )
        self.stdout.write(f"Created order {order}")
