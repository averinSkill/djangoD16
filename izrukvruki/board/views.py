from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView, FormView
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import Post, Reply
from .forms import PostForm, ReplyForm, RepliesFilterForm
from .tasks import reply_send_email, reply_accept_send_email


class PostList(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'


class PostDetails(DetailView):
    model = Post
    template_name = 'post_details.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Reply.objects.filter(author_id=self.request.user.id).filter(post_id=self.kwargs.get('pk')):
            context['respond'] = "Откликнулся"
        elif self.request.user == Post.objects.get(pk=self.kwargs.get('pk')).author:
            context['respond'] = "Мое_объявление"
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.has_perm('board.add_post'):
            return HttpResponseRedirect(reverse('sign_profile'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(id=self.request.user.id)
        post.save()
        return redirect(f'/post/{post.id}')


class PostEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'board.change_post'
    template_name = 'post_edit.html'
    form_class = PostForm
    success_url = '/create/'

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Редактировать объявление может только его автор")

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect('/post/' + str(self.kwargs.get('pk')))


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'board.delete_post'
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/index'

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Удалить объявление может только его автор")


title = str("")


class ReplyList(LoginRequiredMixin, ListView):
    model = Reply
    template_name = 'replies.html'
    context_object_name = 'responses'

    def get_context_data(self, **kwargs):
        context = super(ReplyList, self).get_context_data(**kwargs)
        global title
        """
        Далее в условии - если пользователь попал на страницу через ссылку из письма, в которой содержится
        ID поста для фильтра - фильтр работает по этому ID
        """
        if self.kwargs.get('pk') and Post.objects.filter(id=self.kwargs.get('pk')).exists():
            title = str(Post.objects.get(id=self.kwargs.get('pk')).title)
            print(title)
        context['form'] = RepliesFilterForm(self.request.user, initial={'title': title})
        context['title'] = title
        if title:
            post_id = Post.objects.get(title=title)
            context['filter_replies'] = list(Reply.objects.filter(post_id=post_id).order_by('-d_time'))
            context['replies_post_id'] = post_id.id
        else:
            context['filter_replies'] = list(Reply.objects.filter(post_id__author_id=self.request.user).order_by('-d_time'))
        context['myreplies'] = list(Reply.objects.filter(author_id=self.request.user).order_by('-d_time'))
        return context

    def post(self, request, *args, **kwargs):
        global title
        title = self.request.POST.get('title')

        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/replies')
        return self.get(request, *args, **kwargs)


@login_required
def reply_accept(request, **kwargs):
    if request.user.is_authenticated:
        reply = Reply.objects.get(id=kwargs.get('pk'))
        reply.status = True
        reply.save()
        reply_accept_send_email.delay(reply_id=reply.id)
        return HttpResponseRedirect('/replies')
    else:
        return HttpResponseRedirect('/sign/login')


@login_required
def reply_delete(request, **kwargs):
    if request.user.is_authenticated:
        reply = Reply.objects.get(id=kwargs.get('pk'))
        reply.delete()
        return HttpResponseRedirect('/replies')
    else:
        return HttpResponseRedirect('/sign/login')


class ReplyView(LoginRequiredMixin, CreateView):
    model = Reply
    template_name = 'reply.html'
    form_class = ReplyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        reply = form.save(commit=False)
        reply.author = User.objects.get(id=self.request.user.id)
        reply.post = Post.objects.get(id=self.kwargs.get('pk'))
        reply.save()
        reply_send_email.delay(reply_id=reply.id)
        return redirect(f'/post/{self.kwargs.get("pk")}')


