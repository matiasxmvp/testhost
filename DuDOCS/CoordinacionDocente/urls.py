from django.urls import path
from . import views
from django.contrib import admin
import django

urlpatterns = [
    path('coordinacionDocente/', views.coordinacionDocente, name='coordinacionDocente')
]
