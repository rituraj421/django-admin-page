from django.contrib import admin
from django.urls import path, include
from . import views
admin.site.site_header = "🙂ELECTION COMMISSION🙂"
admin.site.site_title = "EC Admin"
admin.site.index_title = "Welcome to EC RAIT"
urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
]