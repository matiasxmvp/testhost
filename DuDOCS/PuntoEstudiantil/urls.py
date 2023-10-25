from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
import django

urlpatterns = [
    path('puntoEstudiantil/', views.puntoEstudiantil, name='puntoEstudiantil'),
    path('evento/', views.evento, name='evento'),
    path('inventario/', views.inventario, name='inventario'),
    path('prestamos/', views.prestamos, name='prestamos'),
    path('crear_producto/', views.crear_producto, name='crear_producto'),
    path('editar_producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('obtener_producto/<int:producto_id>/', views.obtener_producto, name='obtener_producto'),
    path('crear_prestamo/', views.crear_prestamo, name='crear_prestamo'),
    path('obtener_prestamo/<int:prestamo_id>/', views.obtener_prestamo, name='obtener_prestamo'),
    path('entregar_prestamo/<int:prestamo_id>/', views.entregar_prestamo, name='entregar_prestamo'),
    path('eliminar_prestamo/<int:prestamo_id>/', views.eliminar_prestamo, name='eliminar_prestamo'),
    path('editar_prestamo/<int:prestamo_id>/', views.editar_prestamo, name='editar_prestamo'),
    path('notificar_prestamos/', views.notificar_prestamos, name='notificar_prestamos'),
    path('notificar_prestamo/<int:prestamo_id>/', views.notificar_prestamo, name='notificar_prestamo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
