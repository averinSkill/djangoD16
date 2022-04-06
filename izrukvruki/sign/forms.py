from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.models import User, Group


class BaseRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name')


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        auth_group = Group.objects.get(name='AuthUsers')
        auth_group.user_set.add(user)
        return user


class ConfirmationCodeForm(forms.Form):
    code = forms.CharField(label='Код подтверждения')


