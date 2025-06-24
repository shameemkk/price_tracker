
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('fetch/', views.fetch_html, name='fetch'),
    path('task-status/', views.task_status, name='task_status'),
]
