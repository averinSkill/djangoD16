from datetime import datetime
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.cache import cache

from .models import Post, Category, PostCategory
from .filters import PostFilter
from .forms import PostForm



class NewsList(ListView):
    model = Post
    context_object_name = 'news_list'
    template_name = 'news/news.html'
    ordering = ['-d_time']
    paginate_by = 5
    form_class = PostForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['time_now'] = datetime.utcnow()  # добавим переменную текущей даты time_now
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())

        context['categories'] = Category.objects.all()
        context['form'] = PostForm
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса

        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый товар
            form.save()

        return super().get(request, *args, **kwargs)


class Search(ListView):
    model = Post
    context_object_name = 'search'
    template_name = 'news/search.html'
    paginate_by = 5

    def get_filter(self):
        return PostFilter(self.request.GET, queryset=self.get_queryset())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['time_now'] = datetime.utcnow()
        context['categories'] = Category.objects.all()
        # context['publication'] = PostCategory.objects.get(post=self.kwargs['pk']).category
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())


        return context

class NewsDetail(DetailView):
    model = Post
    context_object_name = 'news_detail'
    template_name = 'news/news_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()  # добавим переменную текущей даты time_now
        context['category'] = Category.objects.all()
        # publication_id = self.kwargs.get('pk')
        # print('publication_id = ', self.kwargs.get('pk'))
        return context

# D8.4
    def get_object(self, *args, **kwargs): # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'news-{self.kwargs["pk"]}', None) # кэш очень похож на словарь, и метод get действует также. Он забирает значение по ключу, если его нет, то забирает None.
        print('OBJ', obj)
        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(*args, **kwargs)
            cache.set(f'news-{self.kwargs["pk"]}', obj)
            print('CACHE', f'news-{self.kwargs["pk"]}')

        return obj


# D6 подписка
class CategoryView(ListView):
    model = Category
    template_name = 'news/post_category.html'
    context_object_name = 'post_category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


# дженерик для создания объекта. Надо указать только имя шаблона и класс формы, который мы написали в прошлом юните. Остальное он сделает за вас
class NewsAdd(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    context_object_name = 'news_create'
    template_name = 'news/news_create.html'
    form_class = PostForm
    success_url = '/news/'


# дженерик для редактирования объекта
class NewsEdit(PermissionRequiredMixin, UpdateView):
    context_object_name = 'news_edit'
    template_name = 'news/news_create.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления товара
class NewsDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    template_name = 'news/news_delete.html'
    context_object_name = 'news_delete'
    queryset = Post.objects.all()
    success_url = '/news/'


@login_required
def add_subscribe(request, pk):

    user = request.user
    id_u = user.id
    category = Category.objects.get(id=pk)
    print(f'''PK =  "{pk}", USER:  "{user}", user_id: "{id_u}", category: "{category}"''')

    qs = category.subscribers.all()
    print('QS= ', qs)
    print('ПОДПИСАН НА КАТЕГОРИЮ ? ', qs.filter(username=user).exists())
    # print(category_object)
    # print(Category.objects.all().filter(postcategory=category))
    # .Post.category.category.subscribers.objects.all().user.username
    if not qs.filter(username=user).exists():
        category.subscribers.add(user)
        print('Пользователь', user, 'подписан на категорию:', category)
    else:
        category.subscribers.remove(user)
        print('Пользователь', user, 'отписался от категории:', category)

    # print('ПОДПИСЧИКИ: ', category.subscribers.all())

    try:
        email = category.subscribers.get(id=id_u).email
        print(f'''email: "{email}" Можно отправить уведомление''')
        send_mail(
            subject=f'News Portal: подписка на обновления категории {category}',
            message=f'«{request.user}», вы подписались на обновление категории: «{category}».',
            from_email='apractikant@yandex.ru',
            recipient_list=[f'{email}', ],
        )

    except Exception as n:
        print('nnnnnnnnnnnnnnnnnnnnn')
    # Category.objects.get(pk=pk).subscribers.add(request.user)
    # print(category.subscribers.all())
    return redirect('/')

#
# @login_required
# def del_subscribe(request, **kwargs):
#     pk = request.GET.get('pk', )
#     print('Пользователь', request.user, 'удален из подписчиков категории:', Category.objects.get(pk=pk))
#     Category.objects.get(pk=pk).subscribers.remove(request.user)
#     return redirect('/news/')
#
#
#
# @login_required
# def subscribe_category(request, pk):
#     user = request.user
#     print('1', user)
#     category = Category.objects.get(id=pk)
#     print('2', category)
#     category.subscribers.add(user)
#     # print('3', category.subscribers.get())
#     id_u = request.user.id
#     print('id_u', id_u)
#     email = category.subscribers.get(id=id_u).email
#     print('email', email)
#     # send_mail(
#     #     subject=f'News Portal: подписка на обновления категории {category}',
#     #     message=f'«{request.user}», вы подписались на обновление категории: «{category}».',
#     #     from_email='apractikant@yandex.ru',
#     #     recipient_list=[f'{email}', ],
#     # )
#     return redirect('/news')
