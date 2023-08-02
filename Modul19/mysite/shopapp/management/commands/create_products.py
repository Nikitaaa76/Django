from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
    Creates new products
    """
    def handle(self, *args, **options):
        self.stdout.write("Create products")
        products_names = [
            "Iphone 10",
            "Iphone 11",
            "Iphone 12",
            "Samsung A54",
            "Samsung A53",
            "Xiaomi 13",
        ]
        for products_name in products_names:
            product, created = Product.objects.get_or_create(name=products_name)
            self.stdout.write(f"Create products {product.name}")
        self.stdout.write(self.style.SUCCESS("Products created"))
