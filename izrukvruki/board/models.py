from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    d_time = models.DateTimeField(auto_now_add=True, verbose_name="Время создания новости")
    title = models.CharField(max_length=255)
    text = models.TextField()
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Автор")
    choices = [
        "Танки",
        "Хилы",
        "ДД",
        "Торговцы",
        "Гилдмастеры",
        "Квестгиверы",
        "Кузнецы",
        "Кожевники",
        "Зельевары",
        "Мастера заклинаний"
    ]

    category = models.CharField(
        choices=choices,
        verbose_name="Категория"
    )

    def __str__(self):
        return f'{self.title}'

    # D8.4 cache
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'news-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его



class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, blank=True)
    d_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.text}'


