from django.urls import path
from .views import *

urlpatterns = [
    
    path("user-register/", user_register, name="user_register"),
    path("user-login/", user_login, name="user_login"),
    path("user-logout/", user_logout, name="user_logout"),
    path("user-profile/<str:username>", user_profile, name="user_profile"),
    path("user-settings/", user_settings, name="user_settings"),
    
    path("post-create/", post_create, name="post_create"),
    path('post-details/<int:pk>', post_details, name="post_details"),
    path('post-edit/<int:pk>', post_edit, name='post_change'),
    path("post-delete/<int:pk>", post_delete, name="post_delete"),
    
    path('', index, name="index"),
]
