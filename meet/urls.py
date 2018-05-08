# coding:utf-8
from django.conf.urls import url
from meet import views


urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^reg/$', views.reg, name="reg"),
    url(r'^$', views.index),
    url(r'^booking/$', views.booking),
    url(r'^log_out/$', views.log_out, name='log_out'),
]
