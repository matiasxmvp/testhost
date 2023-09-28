from django.urls import path
from . import views
from django.contrib import admin
import django

urlpatterns = [
    path('puntoEstudiantil/', views.puntoEstudiantil, name='puntoEstudiantil'),
    path('evento/', views.evento, name='evento'),
    path('inventario/', views.inventario, name='inventario')
]
