from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager

# Modelo para Sede
class Sede(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class UserProfile(models.Model):
    ROLES_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Ayudante', 'Ayudante'),
        ('Docente', 'Docente'),
        ('CoordinadorDocente', 'Coordinador Docente'),
        ('PuntoEstudiantil', 'Punto Estudiantil'),
        ('Dara', 'Dara'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=30, choices=ROLES_CHOICES)
    temp_pass = models.CharField(max_length=30, blank=True, null=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Model Carrera
class Carrera(models.Model):
    nombre = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.nombre
    
# Modelo Malla Curricular
class MallaCurricular(models.Model):
    nombre = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.nombre

# Modelo para Documentos
class Documento(models.Model):
    AREAS_CHOICES = [
        ('Financiamiento', 'Financiamiento'),
        ('IDI', 'IDI'),
        ('CoordinacionDocente', 'CoordinacionDocente'),
        ('AsuntosEstudiantiles', 'AsuntosEstudiantiles'),
        ('Dara', 'Dara'),
    ]

    SEMESTRE_CHOICES = [
        ('1', '1'),
        ('2', '2'),
    ]

    nombre = models.CharField(max_length=255, db_index=True)
    descripcion = models.TextField(max_length=1000)
    archivo = models.BinaryField(null=True)
    area = models.CharField(max_length=255, choices=AREAS_CHOICES, db_index=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, blank=True, null=True, db_index=True)
    year = models.IntegerField(db_index=True, blank=True, null=True)
    semestre = models.CharField(choices=SEMESTRE_CHOICES, db_index=True,blank=True, null=True, max_length=10)  
    malla_curricular = models.ForeignKey(MallaCurricular, on_delete=models.CASCADE,blank=True, null=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE,blank=True, null=True)

    def __str__(self):
        return self.nombre
    
# Modelo para Edificio
class Edificio(models.Model):
    nombre = models.CharField(max_length=255, db_index=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Modelo para Salas
class Sala(models.Model):
    TIPO_CHOICES = [
        ('Teatro', 'Teatro'),
        ('Computación', 'Computación'),
        ('Normal', 'Normal'),
    ]
    nombre = models.CharField(max_length=255, unique=True, db_index=True,blank=True, null=True)
    capacidad = models.IntegerField()
    tipo = models.CharField(choices=TIPO_CHOICES, max_length=255)
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Modelo para Horario de Sala Semestral
class HorarioSala(models.Model):
    fecha = models.DateField(db_index=True)
    hora_inicio = models.TimeField(db_index=True,blank=True, null=True)
    hora_fin = models.TimeField(db_index=True,blank=True, null=True)
    semana = models.IntegerField(db_index=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, db_index=True)
    siglaAsignatura = models.CharField(max_length=255,blank=True, null=True)
    seccion = models.CharField(max_length=10,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    nombreDocente = models.CharField(max_length=255,blank=True, null=True)

# Modelo para Reservas
class Reserva(models.Model):
    horario = models.ForeignKey(HorarioSala, on_delete=models.CASCADE, db_index=True)
    email = models.EmailField()
    nombre = models.CharField(max_length=255, db_index=True)
    fecha = models.DateField()

# Modelo para TNE (Tarjeta Nacional Estudiantil)
class TNE(models.Model):
    nombre = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(db_index=True)
    rut = models.CharField(max_length=12, db_index=True)
    identificador_tarjeta = models.CharField(max_length=12, db_index=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)
    estado = models.CharField(max_length=30,blank=True, null=True)  
    temp_pass = models.CharField(max_length=30,blank=True, null=True)
    def __str__(self):
        return self.identificador_tarjeta

# Modelo para Evento
class Evento(models.Model):
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)
    ayudantes = models.ManyToManyField(UserProfile)
    nombre = models.CharField(max_length=255, db_index=True,blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo para AyudantesEvento
class AyudantesEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    ayudante = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

# Modelo para Asistencia a Evento
class AsistenciaEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    rut_asistente = models.CharField(max_length=12, db_index=True)

# Modelo para Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=255, db_index=True)
    cantidad = models.IntegerField()
    descripcion = models.TextField()
    imagen = models.BinaryField()
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Modelo para Prestamo de producto
class PrestamoProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    email = models.EmailField(db_index=True)
    fecha_prestamo = models.DateTimeField()
    fecha_limite = models.DateTimeField()
    descripcion = models.TextField()
    estado = models.CharField(max_length=30, db_index=True,blank=True, null=True) 