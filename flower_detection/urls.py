from django.urls import path
from . import views

urlpatterns = [
    path('', views.indext, name='indext'),
    path('scan', views.scan, name='scan'),
    path('detect', views.main, name='detect'),
    path('video_on_web', views.video_on_web, name='video_on_web'),
    path('test', views.test, name='test')
]