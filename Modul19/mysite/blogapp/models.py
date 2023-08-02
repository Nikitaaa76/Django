from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _("Authors")

    name = models.CharField(max_length=100, verbose_name="Author")
    bio = models.TextField(null=False, blank=True)


class Category(models.Model):
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _("Categories")

    name = models.CharField(max_length=40, verbose_name="Category")


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name="Tag")

    def __str__(self) -> str:
        return f"Tag(pk={self.pk}, name={self.name!r})"


class Article(models.Model):
    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _("Articles")

    title = models.CharField(max_length=200, verbose_name="Article")
    content = models.TextField(null=False, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    tags = models.ManyToManyField(Tag)
