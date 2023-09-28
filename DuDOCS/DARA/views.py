from django.shortcuts import render, redirect,get_object_or_404
from Core.models import Documento, MallaCurricular, Carrera, Sede
from django.http import FileResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
import io, base64
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import EmailMessage
from Core.models import UserProfile

# Create your views here.
def es_dara(user):
    return user.userprofile.rol == 'Dara'

@login_required
@user_passes_test(es_dara, login_url='/')
def dara(request):
    return render(request,'dara.html')

def subirDocumento(request):
    if request.method == 'POST':
        nuevo_documento = Documento()
        nuevo_documento.nombre = request.POST.get('nombre')
        nuevo_documento.descripcion = request.POST.get('descripcion')
        archivo = request.FILES.get('archivo')
        if archivo:
            nuevo_documento.archivo = archivo.read()
            nuevo_documento.area = request.POST.get('area')
            nuevo_documento.year = request.POST.get('year')
            nuevo_documento.semestre = request.POST.get('semestre')
            nuevo_documento.malla_curricular_id = request.POST.get('malla_curricular')
            nuevo_documento.carrera_id = request.POST.get('carrera')
            nuevo_documento.sede = Sede.objects.get(nombre=request.user.userprofile.sede) 
            nuevo_documento.save()
            response = JsonResponse({'success': True, 'message': f'Documento "{nuevo_documento.nombre}" almacenado con éxito.'})
            return response
    

def descargar_documento(request, documento_id):
    documento = Documento.objects.get(id=documento_id)
    response = FileResponse(io.BytesIO(documento.archivo), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{documento.nombre}.pdf"'
    return response

# Vista para eliminar un documento
@csrf_exempt
def eliminar_documento(request, documento_id):
    documento = Documento.objects.get(id=documento_id)
    if request.method == 'POST':
        nombre_documento = documento.nombre
        documento.delete()
        messages.success(request, f'Documento "{nombre_documento}" eliminado con éxito.')
        response = JsonResponse({'success': True, 'message': f'Documento "{nombre_documento}" eliminado con éxito.'})
        return response

@csrf_exempt
def editar_documento(request, documento_id):
    if request.method == 'POST':
        documento = Documento.objects.get(id=documento_id)
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        area = request.POST.get('area')
        malla_curricular_id = request.POST.get('malla_curricular')
        carrera_id = request.POST.get('carrera')
        semestre = request.POST.get('semestre')
        documento.nombre = nombre
        documento.descripcion = descripcion
        documento.area = area
        documento.malla_curricular_id = malla_curricular_id
        documento.carrera_id = carrera_id
        documento.semestre = semestre

        documento.save()
        return JsonResponse({'success': True, 'message': f'Documento "{nombre}" editado con éxito.'})

@csrf_exempt
def enviar_documento(request):
    if request.method == 'POST':
        documento = Documento.objects.get(id=request.POST.get('documento_id'))
        email = EmailMessage(
            request.POST.get('subject'),
            request.POST.get('message'),
            'dudocs11@gmail.com',
            [request.POST.get('recipient')],
        )
        email.attach(documento.nombre + '.pdf', io.BytesIO(documento.archivo).getvalue())  
        email.send()
        return JsonResponse({'success': True, 'message': f'Documento "{documento.nombre}" enviado con éxito.'})

def subirdocumentos(request):
    mallas_curriculares = MallaCurricular.objects.all()
    carreras = Carrera.objects.all()
    response = render(request, 'subirdocumentos.html', {'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def docsdara(request):
    mallas_curriculares = MallaCurricular.objects.all()
    carreras = Carrera.objects.all()
    documentos_dara = Documento.objects.filter(area='Dara')
    response = render(request, 'docsdara.html', {'documentos': documentos_dara,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def docscoordinaciondocente(request):
    mallas_curriculares = MallaCurricular.objects.all()
    carreras = Carrera.objects.all()
    documentos_cd = Documento.objects.filter(area='CoordinacionDocente')
    response = render(request, 'docscoordinaciondocente.html', {'documentos': documentos_cd,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def docsasuntosestudiantiles(request):
    mallas_curriculares = MallaCurricular.objects.all()
    carreras = Carrera.objects.all()
    documentos_ae = Documento.objects.filter(area='AsuntosEstudiantiles')
    response = render(request, 'docsasuntosestudiantiles.html', {'documentos': documentos_ae,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def docsidi(request):
    mallas_curriculares = MallaCurricular.objects.all()
    carreras = Carrera.objects.all()
    documentos_idi = Documento.objects.filter(area='IDI')
    response = render(request, 'docsidi.html', {'documentos': documentos_idi,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def docsfinanciamiento(request):
    mallas_curriculares = MallaCurricular.objects.all()
    carreras = Carrera.objects.all()
    documentos_financiamiento = Documento.objects.filter(area='Financiamiento')
    response = render(request, 'docsfinanciamiento.html', {'documentos': documentos_financiamiento,'carreras': carreras, 'mallas_curriculares': mallas_curriculares})
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def obtener_documento(request, documento_id):
    doc = get_object_or_404(Documento, id=documento_id)
    # doc = Documento.objects.get(id=documento_id)
    data = {
        'nombre': doc.nombre,
        'descripcion': doc.descripcion,
        'area': doc.area,
        'sede': doc.sede.id if doc.sede else None,
        'year': doc.year,
        'semestre': doc.semestre,
        'malla_curricular': doc.malla_curricular.id if doc.malla_curricular else None,
        'carrera': doc.carrera.id if doc.carrera else None,
    }
    if doc.archivo:
        # Codificar el archivo en base64
        encoded_file = base64.b64encode(doc.archivo).decode('utf-8')
        data['archivo'] = encoded_file
    return JsonResponse(data)