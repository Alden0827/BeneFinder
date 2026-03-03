from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('captcha/', views.captcha_view, name='captcha'),
    path('search/', views.search_view, name='search'),
    path('roster/', views.roster_view, name='roster'),
]
