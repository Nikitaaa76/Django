from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import Group

from .models import Product, Order


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = 'name',


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "delivery_address", "promocode", "user", "products"


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()