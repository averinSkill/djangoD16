from django.urls import path
from django.shortcuts import redirect

from .views import PostList, PostCreate, PostDetails, PostEdit, PostDelete, ReplyList, ReplyView, reply_accept, \
  reply_delete


urlpatterns = [
  path('index', PostList.as_view(), name='index'),
  path('post/<int:pk>', PostDetails.as_view()),
  path('post_create', PostCreate.as_view(), name='post_create'),
  path('post/<int:pk>/edit', PostEdit.as_view()),
  path('post/<int:pk>/delete', PostDelete.as_view()),
  path('replies', ReplyList.as_view(), name='replies'),
  # path('replies/<int:pk>', ReplyList.as_view(), name='replies'),
  path('reply/<int:pk>', ReplyView.as_view(), name='reply'),
  path('reply/accept/<int:pk>', reply_accept),
  path('reply/delete/<int:pk>', reply_delete),
  path('', lambda request: redirect('index', permanent=False)),
]
