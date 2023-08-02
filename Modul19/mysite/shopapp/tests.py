from string import ascii_letters
from random import choices

from django.contrib.auth.models import User, Permission
from django.test import TestCase

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers
from django.urls import reverse


class AddTwoNumbersTestcase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEquals(result, 5)


class ProductCreateViewTestcase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Nikita", password="dsfds", is_superuser=True,)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("Shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "A good table",
                "discount": "10",
            }
        )
        self.assertRedirects(response, reverse("Shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestcase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name="Best Product")

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("Shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_product(self):
        response = self.client.get(
            reverse("Shopapp:product_details", kwargs={"pk": self.product.pk})
        )

        self.assertContains(response, self.product.name)


class OrderDetailViewTestcase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Nikita test", password="dsfdsf")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        permission = Permission.objects.get(codename='view_order')
        self.user.user_permissions.add(permission)
        self.order = Order.objects.create(
            delivery_address="Test address",
            promocode="PromoTest",
            user=self.user,

        )


    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(reverse("Shopapp:order_details", kwargs={'pk': self.order.pk}))
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertTrue(Order.objects.filter(pk=1).exists())


class OrderExportViewTestcase(TestCase):
    fixtures = {
        'users-fixture.json',
        'orders-fixture.json',
        'products-fixture.json',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Nikita", password="dsfdsf", is_staff=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_get_orders_view(self):
        response = self.client.get(reverse('Shopapp:orders_export'))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user': order.user.id,
                'products': list(order.products.values_list('pk', flat=True)),
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(orders_data['orders'], expected_data)

