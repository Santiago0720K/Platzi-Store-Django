from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [  
    # URLs de la API de autenticación
    path('api/register/', views.register_api, name='api_register'),
    path('api/login/', views.login_api, name='api_login'),
    path('api/logout/', views.logout_api, name='api_logout'),
    path('api/profile/', views.user_profile_api, name='api_profile'),
    path('api/check-username/', views.check_username_api, name='api_check_username'),

    # URLs de autenticación basadas en web
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.register_view, name='register'),
]