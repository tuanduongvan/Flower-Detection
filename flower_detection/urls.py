from django.urls import path
from . import views

urlpatterns = [
    path('', views.indext, name='indext'),
    path('scan', views.scan, name='scan'),
    path('detect', views.main, name='detect'),
    path('video_on_web', views.video_on_web, name='video_on_web'),
    path('flower/<int:id>/', views.flower_detail, name='flower_detail'),
    path('flower_modal/<int:id>/', views.flower_modal, name='flower_modal'),
    path('history', views.History, name='history'),
    path('about', views.About, name='about'),
]