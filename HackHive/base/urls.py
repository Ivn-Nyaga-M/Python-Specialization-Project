from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_page, name="home"),  # Home page view

    path('login/', views.login_page, name="login"),
    path('register/', views.register_page, name="register"),
    path('logout/', views.logout_user, name="logout"),
    path('user/<str:pk>/', views.user_page, name="profile"),  # User profile view
    path('event/<str:pk>/', views.event_page, name="event"),  # Event detail view
    path('registration-confirmation/<str:pk>/', views.registration_confirmation, name="registration-confirmation"),  # Event confirmation view
    
    path('account/', views.account_page, name="account"),  # Account page view
    path('project-submission/<str:pk>/', views.project_submission, name="project-submission"),  # Project submission view

    path('update-submission/<str:pk/', views.update_submission, name="update-submission"),
]
