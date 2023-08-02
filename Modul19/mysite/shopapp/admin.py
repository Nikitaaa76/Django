from io import TextIOWrapper
from csv import DictReader
from pyexpat.errors import messages

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .admin_mixins import ExportAsCSVMixin
from .models import Product, Order, ProductImage
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"

    inlines = [
        OrderInline,
        ProductInline,
    ]

    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "price", "name"
    search_fields = "name", "description", "price"
    fieldsets = [
        (None, {
            "fields": ("name", "description"),

        }),
        ("price options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse"),
        }),
        ("Images", {
            "fields": ("preview",),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        })

    ]

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)

        csv_file = TextIOWrapper(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )
        reader = DictReader(csv_file)

        products = [
            Product(**row)
            for row in reader
        ]
        Product.objects.bulk_create(products)
        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv",
            ),
        ]
        return new_urls + urls

    @admin.action(description="Archived products")
    def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
        queryset.update(archived=True)

    @admin.action(description="Unarchived products")
    def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
        queryset.update(archived=False)

    actions = [
        mark_archived,
        mark_unarchived,
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    list_display = ("delivery_address", "promocode", "created_at", "user")

    change_list_template = "shopapp/orders_changelist.html"
    inlines = [
        ProductInline,
    ]

    def get_queryset(self, request):
        return Order.objects.select_related("user")

    def user_verbouse(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)

        csv_file = TextIOWrapper(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )
        reader = DictReader(csv_file)

        orders = []
        for row in reader:
            user_id = int(row['user'])
            user_instance = User.objects.get(pk=user_id)

            order = Order(delivery_address=row['delivery_address'], promocode=row['promocode'],
                          created_at=row['created_at'], user=user_instance)
            orders.append(order)

        Order.objects.bulk_create(orders)
        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import_orders_csv",
            ),
        ]
        return new_urls + urls
