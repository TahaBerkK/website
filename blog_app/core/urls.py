from django.urls import path
from .views import *

urlpatterns = [
    
    path("user-register/", UserRegister.as_view(), name="user_register"),
    path("user-login/", UserLogin.as_view(), name="user_login"),
    path("user-logout/", UserLogout, name="user_logout"),
    path("user-profile/<str:username>", UserProfile.as_view(), name="user_profile"),
    path("user-settings/<str:username>", UserSettings.as_view(), name="user_settings"),
    
    path("post-create/", PostCreate.as_view(), name="post_create"),
    path('post-details/<int:pk>', PostDetails.as_view(), name="post_details"),
    path('post-edit/<int:pk>', PostEdit.as_view(), name='post_change'),
    path("post-delete/<int:pk>", PostDelete.as_view(), name="post_delete"),
    
    path('', IndexView.as_view(), name="index"),

    path("student-datatable/", StudentTable.as_view(), name="student_table"),

    path('error/', PageNotFound.as_view(), name='page_not_found')

]
