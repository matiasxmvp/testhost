from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test, login_required

# Create your views here.
def es_docente_o_coordinador_docente(user):
    return user.userprofile.rol in ['Docente', 'Coordinador Docente']

@login_required
@user_passes_test(es_docente_o_coordinador_docente, login_url='/')
def coordinacionDocente(request):
    return render(request,'coordinacionDocente.html')