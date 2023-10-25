from django.shortcuts import render, redirect,get_object_or_404, HttpResponse
from Core.models import PrestamoProducto, Producto, Sede
from django.http import FileResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.utils import timezone
from itertools import cycle


# Create your views here.
def es_ayudante_o_punto_estudiantil(user):
    return user.userprofile.rol in ['Ayudante', 'PuntoEstudiantil']

@login_required
@user_passes_test(es_ayudante_o_punto_estudiantil, login_url='/')
def puntoEstudiantil(request):
    return render(request,'puntoEstudiantil.html')

def evento(request):
    response = render(request, 'evento.html')
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def inventario(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:
        productos = Producto.objects.all()
        response = render(request, 'inventario.html', {'productos': productos})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')

def prestamos(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and 'http://127.0.0.1:8000' in referer:
        prestamos = PrestamoProducto.objects.all()
        response = render(request, 'prestamos.html', {'prestamos': prestamos})
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    else:
        return redirect('/')

def obtener_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    data = {
        'nombre': producto.nombre,
        'imagen': producto.imagen.url,
        'descripcion': producto.descripcion,
        'cantidad_total': producto.cantidad_total,
        'cantidad_disponible': producto.cantidad_disponible,
    }
    return JsonResponse(data)
    
def crear_producto(request):
    if request.method == 'POST':
        try:
            nuevo_producto = Producto()
            sede = Sede.objects.get(nombre=request.user.userprofile.sede)
            imagen = request.FILES.get('imagenprod')
            nuevo_producto.cantidad_total = int(request.POST.get('cantidad_total'))
            nuevo_producto.cantidad_disponible = int(request.POST.get('cantidad_disponible'))
            nuevo_producto.nombre = request.POST.get('nombre')
            if Producto.objects.filter(nombre=nuevo_producto.nombre).exists():
                raise ValidationError('El nombre de producto ya existe')  
            if  nuevo_producto.cantidad_disponible < 0 or nuevo_producto.cantidad_total < 0:
                raise ValidationError('El stock debe no puede ser menor que 0')
            if nuevo_producto.cantidad_disponible > nuevo_producto.cantidad_total:
                raise ValidationError('El stock disponible no puede ser mayor que el stock total')      
            if imagen:
                file_name = f'productos/{nuevo_producto.nombre}.jpg'
                file_content = imagen.read()
                default_storage.save(file_name, ContentFile(file_content))
                nuevo_producto.imagen = file_name
            else:
                nuevo_producto.nombre = request.POST.get('nombre')
                nuevo_producto.imagen = 'productos/noimage.jpg'
            nuevo_producto.nombre = request.POST.get('nombre')
            nuevo_producto.descripcion = request.POST.get('descripcion')
            nuevo_producto.cantidad_total = request.POST.get('cantidad_total')
            nuevo_producto.cantidad_disponible = request.POST.get('cantidad_disponible')
            nuevo_producto.sede = sede        
            nuevo_producto.save()
            return JsonResponse({'success': 'Producto creado con éxito'})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        try:
            imagen = request.FILES.get('editImagen')
            nombre = request.POST['editNombre']
            descripcion = request.POST['editDescripcion']
            cantidad_total = int(request.POST['editCantidadTotal'])
            cantidad_disponible = int(request.POST['editCantidadDisponible'])

            if not all([nombre, descripcion, cantidad_disponible, cantidad_total]):
                raise ValidationError('Todos los campos son necesarios')

            if producto.nombre != nombre:
                if Producto.objects.filter(nombre=nombre).exists():
                    raise ValidationError('El nombre de producto ya existe')    
            producto.nombre = nombre
            producto.descripcion = descripcion
            if imagen:
                producto.imagen = imagen
            producto.cantidad_disponible = cantidad_disponible
            producto.cantidad_total = cantidad_total
            producto.save()

            return JsonResponse({'success': True, 'message': f'Producto "{nombre}" editado con éxito.'})

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
# Vista para eliminar un producto
def eliminar_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado con éxito.')
        response = JsonResponse({'success': True, 'message': f'Producto "{nombre_producto}" eliminado con éxito.'})
        return response
    
def obtener_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(PrestamoProducto, id=prestamo_id)
    data = {
        'email': prestamo.email,
        'rut': prestamo.rut,
        'producto': prestamo.producto.nombre,
        'nombre': prestamo.nombre,
        'cantidad': prestamo.cantidad,
        'fecha_limite': prestamo.fecha_limite,
        'fecha_prestamo': prestamo.fecha_prestamo,
        'estado': prestamo.estado,
    }
    return JsonResponse(data)
    
def eliminar_prestamo(request, prestamo_id):
    prestamo = PrestamoProducto.objects.get(id=prestamo_id)
    producto = get_object_or_404(Producto, nombre=prestamo.producto.nombre)
    if request.method == 'POST':
        producto.cantidad_disponible += int(prestamo.cantidad)
        producto.save()
        prestamo.delete()
        messages.success(request, f'Prestamo eliminado con éxito.')
        response = JsonResponse({'success': True, 'message': f'Prestamo eliminado con éxito.'})
        return response

def crear_prestamo(request):
    if request.method == 'POST':
        try:
            prestamo = PrestamoProducto()
            
            # Obtén el nombre del producto directamente desde el formulario
            producto_nombre = request.POST.get('producto')

            # Obtén el producto utilizando el nombre
            producto = Producto.objects.get(nombre=producto_nombre)

            # Obtén la cantidad y otros campos desde el formulario
            prestamo.producto = producto
            prestamo.cantidad = int(request.POST.get('cantidad'))
            prestamo.email = request.POST.get('email')
            prestamo.rut = request.POST.get('rut')
            prestamo.nombre = request.POST.get('nombre')
            prestamo.estado = "En Curso"

            fecha_limite_str = request.POST.get('fecha_limite') # formato recibido: yyyy-mm-dd
            fecha_prestamo = timezone.now()

            # Convierte la fecha límite a objeto datetime
            fecha_limite = datetime.strptime(fecha_limite_str, "%Y-%m-%d")


            fecha_prestamo = fecha_prestamo.replace(hour=00, minute=0, second=1)
            # Añade las horas 23:59 a la fecha límite
            fecha_limite = fecha_limite.replace(hour=23, minute=59, second=59)
            fecha_limite = timezone.make_aware(fecha_limite, timezone.get_default_timezone())

            if fecha_limite < fecha_prestamo:
                raise ValidationError('La fecha límite debe ser mayor que la fecha actual')

            # Asigna las fechas al prestamo
            prestamo.fecha_prestamo = fecha_prestamo
            prestamo.fecha_limite = fecha_limite

            if prestamo.cantidad <= 0 or prestamo.cantidad > producto.cantidad_disponible:
                raise ValidationError('Cantidad inválida')

            if not validar_rut(prestamo.rut):
                raise ValidationError('Rut inválido')

            # Resta la cantidad del préstamo de la cantidad disponible del producto
            producto.cantidad_disponible -= prestamo.cantidad
            producto.save()

            # Guarda el prestamo
            prestamo.save()

            return JsonResponse({'success': 'Préstamo creado con éxito'})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

def editar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(PrestamoProducto, id=prestamo_id)
    producto = get_object_or_404(Producto, nombre=prestamo.producto.nombre)
    if request.method == 'POST':
        try:
            email = request.POST['editemail']
            rut = request.POST['editrut']
            nombre = request.POST['editnombre']
            cantidad = int(request.POST['editcantidad'])
            fecha_limite_str = request.POST.get('editfechalimite')
            # Convert the date to datetime object
            fecha_limite = datetime.strptime(fecha_limite_str, "%Y-%m-%d")

            # Make it timezone aware (we use the default timezone here)
            fecha_limite = timezone.make_aware(fecha_limite)

            fecha_limite = fecha_limite.replace(hour=23, minute=59, second=59)
            prestamo.fecha_prestamo = prestamo.fecha_prestamo.replace(hour=0, minute=0, second=1)

            # Check if the deadline is later than the current date
            if fecha_limite < prestamo.fecha_prestamo:
                raise ValidationError('La fecha límite debe ser mayor que la fecha actual')
            
            if prestamo.cantidad != cantidad:
                if cantidad <= 0 or cantidad > int(prestamo.producto.cantidad_disponible) + int(prestamo.cantidad):
                    raise ValidationError('Cantidad inválida')
                else:
                    producto.cantidad_disponible += prestamo.cantidad
                    prestamo.cantidad = cantidad
                    producto.cantidad_disponible -= prestamo.cantidad

            if not validar_rut(rut):
                raise ValidationError('Rut inválido')
            
            prestamo.email = email
            prestamo.rut = rut
            prestamo.nombre = nombre
            prestamo.fecha_limite = fecha_limite
            producto.save()
            prestamo.save()

            return JsonResponse({'success': True, 'message': f'Prestamo editado con éxito.'})

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
def entregar_prestamo(request, prestamo_id):
    prestamo = get_object_or_404(PrestamoProducto, id=prestamo_id)
    producto = get_object_or_404(Producto, nombre=prestamo.producto.nombre)
    if request.method == 'POST':
        try:
            producto.cantidad_disponible += int(prestamo.cantidad)
            producto.save()
            prestamo.delete()
            messages.success(request, f'Prestamo eliminado con éxito.')
            response = JsonResponse({'success': True, 'message': f'Prestamo eliminado con éxito.'})
            return response      
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
def notificar_prestamo(request, prestamo_id):
    if request.method == 'POST':
        try:
            prestamo = get_object_or_404(PrestamoProducto, id=prestamo_id)
        except:
            return JsonResponse({'error': 'Email erroneo'}, status=400)
        recipient = prestamo.email
        message = f'Tiene un préstamo atrasado con fecha de devolución {prestamo.fecha_limite} ' \
                  f'del producto {prestamo.producto.nombre}, cantidad: {prestamo.cantidad}. ' \
                  f'Favor acercarse a Punto Estudiantil para realizar la devolución.'

        # Crea y envía el email
        email = EmailMessage(
            'Notificación de préstamo atrasado',  # Asunto por defecto
            message,  # Mensaje por defecto
            'dudocs11@gmail.com',
            [recipient],
        )
        email.send()
        return JsonResponse({'success': True, 'message': f'Notificaciones enviadas con éxito.'})

def notificar_prestamos(request):
    if request.method == 'POST':
        now = timezone.now()
    
        # Filtra todos los préstamos cuya fecha de devolución sea menor o igual a la fecha actual
        # prestamos_atrasados = PrestamoProducto.objects.filter(fecha_limite__lte=now)
        prestamos_atrasados = PrestamoProducto.objects.filter(estado="Atrasado")

        if not prestamos_atrasados.exists():
            return JsonResponse({'success': False, 'message': 'No se encontraron préstamos atrasados, no se enviaron notificaciones.'})

        if prestamos_atrasados:
            # Crea un mensaje para notificar a todos los usuarios con préstamos atrasados
            message = 'Tiene(s) un(os) préstamo(s) atrasado(s):\n\n favor dirigerse a Punto Estudiantil para realizar la devolución de los objetos solicitados.' 
            # Obtiene los destinatarios únicos de los préstamos atrasados
            recipients = prestamos_atrasados.values_list('email', flat=True).distinct()

            # Envia el mensaje a todos los destinatarios
            email = EmailMessage(
                'Notificación de préstamos atrasados',  # Asunto por defecto
                message,  # Mensaje con detalles de los préstamos atrasados
                'dudocs11@gmail.com',
                recipients,
            )
            email.send()
            return JsonResponse({'success': True, 'message': f'Se enviaron notificaciones con éxito a {len(recipients)} correos.'})
    
def validar_rut(rut):
    rut = rut.upper();
    rut = rut.replace("-", "")
    rut = rut.replace(".", "")
    aux = rut[:-1]
    dv = rut[-1:]

    reversed_digits = map(int, reversed(str(aux)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    res = (-s) % 11

    if str(res) == dv:
        return True
    elif (res == 10) and (dv == 'K'):
        return True
    else:
        return False