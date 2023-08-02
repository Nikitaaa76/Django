import logging
from timeit import default_timer

from django.core.serializers import serialize
from django.core.cache import cache
from django.contrib.syndication.views import Feed
from django.contrib.auth.models import Group, User
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, Http404
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse


from myauth.models import Profile
from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer

log = logging.getLogger(__name__)


@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    A set of views for product actions.
    Full CRUD for product entities
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @extend_schema(
        summary='Get one product by ID',
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description='Empty response, product by id not found'),
        }

    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["user", "delivery_address"]
    filterset_fields = [
        "user",
        "delivery_address",
        "promocode",
        "products",
    ]
    ordering_fields = [
        "user",
        "delivery_address",
        "products",
    ]


def main_menu(request):
    return render(request, 'shopapp/main-menu.html')


class ShopIndexView(View):
    def get(self, request: HttpRequest):
        products = [
            ('Iphone 10', 1000),
            ('Iphone 11', 1100),
            ('Iphone 12', 1200),
            ('Samsung A54', 800),
            ('Samsung A53', 750),
            ('Xiaomi 13', 850),
        ]
        context = {
            "products": products,
            "time_running": default_timer(),
            "items": 1,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest):
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/products-details.html'
    #model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    #model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductsCreateView(UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.groups.filter(name="editing_product").exists() or self.request.user.is_superuser

    permission_required = "add_product"
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy('Shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    def test_func(self):
        return self.request.user.groups.filter(name="editing_product").exists() or self.request.user.is_superuser

    permission_required = "update_product"
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_superuser:
            if obj.created_by != request.user:
                return HttpResponseForbidden("You don't have rights to edit the product")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'Shopapp:product_details',
            kwargs={"pk": self.object.pk}
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('Shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save(update_fields=['archived'])
        return HttpResponseRedirect(success_url)


class OrdersCreateView(CreateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    success_url = reverse_lazy('Shopapp:order_list')


class OrdersCUpdateView(UpdateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            'Shopapp:order_details',
            kwargs={"pk": self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('Shopapp:order_list')


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.select_related("user").prefetch_related('products')
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects.select_related("user").prefetch_related('products')
    )


class OrderExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by('pk').all()
        orders_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user': order.user.id,
                'products': list(order.products.values_list('pk', flat=True)),
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})


class ProductsExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by('pk').all()
        products_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': product.price,
                'archived': product.archived,
            }
            for product in products
        ]
        return JsonResponse({'orders': products_data})


class LatestProductsFeed(Feed):
    name = "Products"
    description = "Update products"
    link = reverse_lazy("Shopapp:products_list")

    def items(self):
        return (
            Product.objects
            .filter(archived=False)
            .order_by("-archived")[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_link(self, item: Product):
        return reverse('Shopapp:products_list')


class UserOrdersListView(UserPassesTestMixin, ListView):
    def test_func(self):
        return self.request.user.is_authenticated

    model = Order
    template_name = "shopapp/orders-from-user.html"
    context_object_name = "user_orders"

    def get_queryset(self):
        self.owner = User.objects.get(pk=self.kwargs['user_id'])
        return Order.objects.filter(user=self.owner)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context

    @cache_page(60 * 3, key_prefix='user_orders')
    def orders_from_user(request):
        user_orders = Order.objects.filter(user=request.user)
        context = {
            'owner_orders': user_orders,
            'owner': request.user,
        }
        return render(request, 'orders-from-user.html', context)


class UserOrdersExportView(View):
    def get(self, request, user_id):
        try:
            user_orders_cache_key = f"user_orders_{user_id}"
            cached_data = cache.get(user_orders_cache_key)
            if cached_data:
                return JsonResponse(cached_data, safe=False)

            user = User.objects.get(id=user_id)
            orders = Order.objects.filter(user_id=user_id).order_by('id')
            if not orders:
                raise Http404

            data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'orders': serialize('json', orders),
            }

            cache.set(user_orders_cache_key, data, 200)

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)})
