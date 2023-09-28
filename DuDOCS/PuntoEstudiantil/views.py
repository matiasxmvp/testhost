from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test, login_required


# Create your views here.
def es_ayudante_o_punto_estudiantil(user):
    return user.userprofile.rol in ['Ayudante', 'Punto Estudiantil']

@login_required
@user_passes_test(es_ayudante_o_punto_estudiantil, login_url='/')
def puntoEstudiantil(request):
    return render(request,'puntoEstudiantil.html')

def evento(request):
    response = render(request, 'evento.html')
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def inventario(request):
    response = render(request, 'inventario.html')
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response