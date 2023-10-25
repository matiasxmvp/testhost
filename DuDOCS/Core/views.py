from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .jobs import check_prestamos, check_reservas

# Verificar prestamos atrasados
scheduler_prestamos = BackgroundScheduler()
scheduler_prestamos.add_job(check_prestamos, 'interval', days=1, start_date='2023-10-24 00:00:01')
scheduler_prestamos.start()

# Eliminar reservas al completarse
scheduler_reservas = BackgroundScheduler()
dias = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat']
horas = ['8:01', '8:41', '9:31', '10:11', '11:01', '11:41', '12:31', '13:11', '14:01', '14:41',
         '15:31', '16:11', '17:01', '17:41', '18:21', '19:11', '19:51', '20:41', '21:21', '22:11']
for dia in dias:
    for hora in horas:
        trigger = CronTrigger(day_of_week=dia, hour=hora.split(':')[0], minute=hora.split(':')[1])
        scheduler_reservas.add_job(check_reservas, trigger)
scheduler_reservas.start()

# Create your views here.
@login_required(login_url='/')
def inicio(request):
    return render(request,'inicio.html')

def error(request, exception):
    return render(request,'error.html', status=404)
