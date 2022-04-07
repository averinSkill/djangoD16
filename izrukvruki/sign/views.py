from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import UpdateView, FormView
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .forms import BaseRegisterForm, ConfirmationCodeForm
import random
import string


code = ""

@login_required
def confirmation_code(request):
    global code
    code = ""

    if not CustomUser.objects.filter(user=request.user).exists():
        add_user = CustomUser()
        add_user.user = request.user
        add_user.save()

    user = CustomUser.objects.get(user=request.user)
    user.code = ''.join(random.sample(string.ascii_letters, 6))
    user.save()
    # скопируйте следующий код и вставьте в форму подтверждения на странице
    send_mail(
        subject=f'Подтверждение регистрации',
        message=f'Здравствуйте, {request.user}! Для подтверждения регистрации, введите код {user.code} на '
                f'странице регистрации\nhttp://127.0.0.1:8000/accounts/profile',
        from_email='apractikant@yandex.ru',
        recipient_list=[request.user.email, ],
    )
    print(f"подтверждение регистрации отправлено на {request.user.email}")
    return HttpResponseRedirect(reverse('sign_profile'))


class ProfileUserView(LoginRequiredMixin, FormView):
    template_name = 'sign/profile.html'
    form_class = ConfirmationCodeForm

    def dispatch(self, request, *args, **kwargs):
        print("============", self.request.user)
        if CustomUser.objects.filter(user=self.request.user).exists():
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('confirmation_code'))

    def form_valid(self, form, **kwargs):
        global code
        if form.cleaned_data['code'] == CustomUser.objects.get(user=self.request.user).code:
            Group.objects.get(name='AuthUsers').user_set.add(self.request.user)
        else:
            code = "Введен неверный код подтверждения"
        return HttpResponseRedirect(reverse('sign_profile'))

    def get_context_data(self, **kwargs):
        context = super(ProfileUserView, self).get_context_data(**kwargs)
        context['code'] = code
        if self.request.user.groups.filter(name='AuthUsers').exists():
            context['auth'] = True
        else:
            context['auth'] = False
        return context


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/sign/profile'
    template_name = 'sign/update.html'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
          queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)
