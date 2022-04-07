from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    d_time = models.DateTimeField(auto_now_add=True, verbose_name="Время создания объявления")
    title = models.CharField(max_length=255)
    text = RichTextField()
    choices = [
        ("TK", "Танки"),
        ("HL", "Хилы"),
        ("DD", "ДД"),
        ("TR", "Торговцы"),
        ("GD", "Гилдмастеры"),
        ("KG", "Квестгиверы"),
        ("KC", "Кузнецы"),
        ("KG", "Кожевники"),
        ("ZV", "Зельевары"),
        ("MZ", "Мастера заклинаний")
    ]

    category = models.CharField(
        max_length=2,
        choices=choices,
        verbose_name="Категория"
    )


class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст')
    status = models.BooleanField(default=False)
    d_time = models.DateTimeField(auto_now_add=True)

