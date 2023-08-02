from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ShopIndexView,
    GroupsListView,
    ProductsListView,
    OrdersListView,
    OrdersCreateView,
    ProductDetailsView,
    OrderDetailView,
    ProductsCreateView,
    ProductUpdateView,
    ProductDeleteView,
    OrdersCUpdateView,
    OrderDeleteView,
    main_menu,
    OrderExportView,
    ProductViewSet,
    OrderViewSet,
    ProductsExportView,
    LatestProductsFeed,
    UserOrdersListView,
    UserOrdersExportView
)

app_name = 'Shopapp'

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    path('', main_menu, name="main-menu"),
    path('shop/', ShopIndexView.as_view(), name="index"),
    path('api/', include(routers.urls)),
    path('api/orders/', include(routers.urls)),
    path('shop/groups/', GroupsListView.as_view(), name="groups_list"),
    path('shop/products/', ProductsListView.as_view(), name="products_list"),
    path('shop/products/latest/feed/', LatestProductsFeed(), name="products-feed"),
    path('shop/products/export/', ProductsExportView.as_view(), name="products_export"),
    path('shop/products/create/', ProductsCreateView.as_view(), name="product_create"),
    path('shop/products/<int:pk>/', ProductDetailsView.as_view(), name="product_details"),
    path('shop/products/<int:pk>/update', ProductUpdateView.as_view(), name="product_update"),
    path('shop/products/<int:pk>/archived', ProductDeleteView.as_view(), name="product_delete"),
    path('shop/orders/', OrdersListView.as_view(), name="order_list"),
    path('shop/<int:user_id>/orders/', UserOrdersListView.as_view(), name='orders-from-user.html'),
    path('shop/orders/export/', OrderExportView.as_view(), name="orders_export"),
    path('shop/<int:user_id>/orders/export/', UserOrdersExportView.as_view(), name='user_orders_export'),
    path('shop/orders/create/', OrdersCreateView.as_view(), name="order_create"),
    path('shop/orders/<int:pk>/', OrderDetailView.as_view(), name="order_details"),
    path('shop/orders/<int:pk>/update', OrdersCUpdateView.as_view(), name="order_update"),
    path('shop/orders/<int:pk>/delete', OrderDeleteView.as_view(), name="order_delete"),
]

