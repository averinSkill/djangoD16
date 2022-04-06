from django import forms
from .models import Post, Reply


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {'title': forms.TextInput(attrs={'size': '70'})}
        fields = ('category', 'title', 'text',)

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['category'].label = "Категория:"
        self.fields['title'].label = "Заголовок"
        self.fields['text'].label = "Текст объявления:"


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = "Текст отклика:"


class RepliesFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(RepliesFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Объявление',
            queryset=Post.objects.filter(author_id=user.id).order_by('-d_time').values_list('title', flat=True),
            empty_label="Все",
            required=False
        )
