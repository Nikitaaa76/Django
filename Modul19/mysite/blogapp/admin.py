from django.contrib import admin
from .models import Article, Author, Tag, Category


@admin.register(Article)
class AuthorAdmin(admin.ModelAdmin):
    list_display = "pk", "author", "title", "content", "category", "pub_date"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = "pk", "name", "bio"


@admin.register(Tag)
class AuthorAdmin(admin.ModelAdmin):
    list_display = "pk", "name"


@admin.register(Category)
class AuthorAdmin(admin.ModelAdmin):
    list_display = "pk", "name"
