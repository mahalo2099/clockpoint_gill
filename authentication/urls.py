from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('register_attendance', views.register_attendance, name='register_attendance'),
    path('signin', views.signin, name='signin'),
    path('register_check_in', views.register_check_in, name='register_check_in'),
    path('register_check_out', views.register_check_out, name='register_check_out'),
    # path('register_point', views.register_point, name='register_point'),
    path('monthly_report', views.monthly_report, name='monthly_report'),
    path('signout', views.signout, name='signout'),
    path('activate/<uidb64>/<token>', views.activate, name="activate")  
]