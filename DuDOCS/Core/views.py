from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

# Create your views here.
@login_required(login_url='/')
def inicio(request):
    return render(request,'inicio.html')

def error(request, exception):
    return render(request,'error.html', status=404)
