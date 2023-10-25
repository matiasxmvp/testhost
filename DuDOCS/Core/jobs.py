from django.utils import timezone
from .models import PrestamoProducto, HorarioSala

def check_prestamos():
    for prestamo in PrestamoProducto.objects.filter(estado='En Curso'):
        if timezone.now() > prestamo.fecha_limite and prestamo.estado != 'Atrasado':
            prestamo.estado = 'Atrasado'
            prestamo.save()

def check_reservas():
    fecha_actual = timezone.now().date()
    for horario in HorarioSala.objects.filter(tipo_hora='Reserva', fecha=fecha_actual):
        if timezone.now().time() > horario.hora_fin:
            horario.delete()