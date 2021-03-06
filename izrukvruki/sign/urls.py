from django.urls import path, include
from .views import ProfileUserView, UpdateProfile, confirmation_code


urlpatterns = [
  path('profile', ProfileUserView.as_view(), name='sign_profile'),
  path('edit', UpdateProfile.as_view(), name='sign_edit'),
  path('confirmation_code', confirmation_code, name='confirmation_code'),
  path('', include('allauth.urls')),
]

