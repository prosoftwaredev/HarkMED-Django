from django.conf.urls import *
from django.conf.urls import include, url
from django.contrib import admin
from . import views

handler404 = 'harkmed.views.custom_404'

appname= "main"
urlpatterns = [
    url(r'^faq/$', views.FaqView.as_view(), name='faq'),

]