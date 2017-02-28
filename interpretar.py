# -*- coding: utf-8 -*-
from django.core.management import BaseCommand
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random


class Command(BaseCommand):
    # help = "My test command"

    def handle(self, *args, **options):
        # self.stdout.write("Doing All The Things!")
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            './asuntos-jurisdiccionales-c8bf36cb780c.json', scope)
        gc = gspread.authorize(credentials)
        sh = gc.open('Proyecto radicacion')
        worksheet = sh.worksheet("Flujo Super")
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        # opens file with name of "test.txt"
        worksheet = worksheet.get_all_values()
        row = len(worksheet)
        j = 1
        model = True
        f1 = open('principal/views.py', "w")
        f2 = open('principal/forms.py', "w")
        f3 = open('principal/models.py', "w")
        f4 = open('principal/automatico.py', "w")

        views = """


# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, render_to_response, RequestContext, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import logout
from .models import Proceso, Entrada, Usuarios, Aviso, Salida, Imprimir, Opciones, Titulo, Historia, Cont_autos
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from django.db.models import When, F, Q
from django.utils import timezone

def demo():
    user, created = User.objects.get_or_create(
        username="radicador", email="radicador@radicador.com")
    if created:
        user.set_password("123")
        Usuarios.objects.get_or_create(
            user=user, rol="radicador", email="radicador@radicador.com", numero_documento="1")
        user.save()

    user, created = User.objects.get_or_create(
        username="secretaria", email="secretaria@secretaria.com")
    if created:
        user.set_password("123")
        Usuarios.objects.get_or_create(
            user=user, rol="secretaria", email="secretaria@secretaria.com", numero_documento="2")
        user.save()

    user, created = User.objects.get_or_create(
        username="subdirector", email="subdirector@subdirector.com")
    if created:
        user.set_password("123")
        Usuarios.objects.get_or_create(
            user=user, rol="subdirector", email="subdirector@subdirector.com", numero_documento="3")
        user.save()

    user, created = User.objects.get_or_create(
        username="abogado", email="abogado@abogado.com")
    if created:
        user.set_password("123")
        Usuarios.objects.get_or_create(
            user=user, rol="abogado", email="abogado@abogado.com", numero_documento="4")
        user.save()
 
    user, created = User.objects.get_or_create(
        username="ciudadano", email="ciudadano@ciudadano.com")
    if created:
        user.set_password("123")
        Usuarios.objects.get_or_create(
            user=user, rol="ciudadano", email="ciudadano@ciudadano.com", numero_documento="5ciudadano", nombres="Nombres", apellidos="Apellidos")
        user.save()

@login_required
def imprimir(request):
    usuario = Usuarios.objects.get(user__id=request.user.id)
    imprimir2 = Imprimir.objects.filter(visto="no", rol=usuario.rol).order_by('-id')
    imprimir3 = Imprimir.objects.filter(
        visto="no", usuario=str(usuario.user.id)).order_by('-id')
    imprimir = imprimir2 | imprimir3
    if request.user.is_superuser:
        imprimir = imprimir | Imprimir.objects.filter(visto="no").order_by('-id')
    cola = []
    cola2 = []
    for i in imprimir:
        if not [i.titulo_pantalla, i.proceso] in cola2:
            cola.append([i.created_at, i.titulo_pantalla, i.proceso, i.pantalla])
            cola2.append([ i.titulo_pantalla, i.proceso])
    imprimir = cola

    imprimir_leidos2 = Imprimir.objects.filter(visto="si", rol=usuario.rol).order_by('-id')
    imprimir_leidos3 = Imprimir.objects.filter(
        visto="si", usuario=str(usuario.user.id)).order_by('-id')
    imprimir_leidos = imprimir_leidos2 | imprimir_leidos3
    if request.user.is_superuser:
        imprimir_leidos = imprimir_leidos | Imprimir.objects.filter(visto="si").order_by('-id')
    cola3 = []
    cola23 = []
    for i in imprimir_leidos:
        if not [i.titulo_pantalla, i.proceso] in cola23:
            cola3.append([i.created_at, i.titulo_pantalla, i.proceso, i.pantalla])
            cola23.append([ i.titulo_pantalla, i.proceso])
    imprimir_leidos = cola3
        
        
    return render(request, 'imprimir.html', {'imprimir': imprimir, 'imprimir_leidos': imprimir_leidos})



@login_required
def imprimir_detalle(request, id, entrada):
    usuario = Usuarios.objects.get(user__id=request.user.id)
    imprimir2 = Imprimir.objects.filter(proceso=id, rol=usuario.rol,pantalla=entrada)
    imprimir3 = Imprimir.objects.filter(
       proceso=id, usuario=str(usuario.user.id),pantalla=entrada)
    imprimir = imprimir2 | imprimir3
    if request.user.is_superuser:
        imprimir = imprimir | Imprimir.objects.filter(proceso=id,pantalla=entrada)
    
    imprimir_detalle = imprimir[0]
        
    return render(request, 'imprimir_detalle.html', {'imprimir': imprimir, 'imprimir_detalle':imprimir_detalle})



@login_required
def index(request):
    demo()
    user = User.objects.get(id=request.user.id)
    if request.user.is_superuser and request.user.id ==1:
        Usuarios.objects.get_or_create(nombres="nombresadmin", apellidos="apellidosadmin",
                                       user=user, rol="admin", email="admin@admin.com", numero_documento="5")
    # perfil_up = Perfil.objects.filter(user=user).update(rol="radicador")
    return redirect('/procesos')


def login(request):
    demo()
    return render(request, 'login.html', {})


@login_required
def logout(request):
    logout(request)
    return redirect('/')


@login_required
def entrada_crear(request, id):
    try:
        usuarios = Usuarios.objects.get(user__id=request.user.id)
    except:
        usuarios = None
    form = EntradaForm(request.POST or None,
                       request.FILES or None)
    try:
        proceso = Proceso.objects.get(id=id)
    except:
        return redirect('/')
    user_okay = 0
    if usuarios.rol == "radicador":
        user_okay = 1
    if request.user.is_superuser:
        user_okay = 1
    if request.method == 'POST' and user_okay > 0:
        if form.is_valid():
            entrada = form.save()
            Entrada.objects.filter(id=entrada.id).update(proceso=proceso.id)

            messages.add_message(
                request, messages.INFO, 'Entrada guardada.')
            return redirect('/procesos')
    return render(request, 'entrada_crear.html', {'form': form, 'proceso': proceso})


@login_required
def crear_usuarios(request):
    usuarios = Usuarios.objects.get(user__id=request.user.id)
    form = usuariosForm(request.POST or None,
                        request.FILES or None)
    user_okay = 0
    if usuarios.rol == "radicador":
        user_okay = 1
    if usuarios.rol == "secretaria":
        user_okay = 1
    if usuarios.rol == "subdirector":
        user_okay = 1
    if request.user.is_superuser:
        user_okay = 1
    if user_okay == 0:
        return redirect('/')
    if request.method == 'POST' and user_okay > 0:
        if form.is_valid():
            usuarios = form.save()
            user = User.objects.create_user(username=request.POST['numero_documento'],
                                            email=request.POST['email'],
                                            password=request.POST['password'])
            usuarios2 = Usuarios.objects.filter(
                id=usuarios.id).update(user=user)
            messages.add_message(
                request, messages.INFO, 'Usuario con el Nombre:'+str("Nombre Apellido") + " creado.")
            return redirect('/usuarios')
    return render(request, 'usuarios_crear.html', {'form': form})


@login_required
def usuarios(request):
    usuarios = Usuarios.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})


def historia(request, id):
    proceso = Proceso.objects.get(id=id)
    historias = Historia.objects.filter(proceso=proceso.id)
    return render(request, 'historia.html', {'historias': historias, 'proceso': proceso.id})


@login_required
def crear(request):
    user = User.objects.get(id=request.user.id)
    proceso = Proceso.objects.create(user=user)
    entrada = Entrada.objects.create(proceso=proceso.id)
    opciones = Opciones.objects.create(proceso=proceso.id, estado='1')
    messages.add_message(
        request, messages.INFO, 'Proceso iniciado con id:'+str(proceso.id))
    return redirect('/procesos')


@login_required
def tarea_async(request, proceso, tarea):
    try:
        usuarios = Usuarios.objects.get(user__id=request.user.id)
    except:
        return redirect('/')
    try:
        proceso = Proceso.objects.get(id=proceso)
    except:
        return redirect('/')
    user_okay = 0
    if usuarios.rol == "secretaria":
        user_okay = 1
    if request.user.is_superuser:
        user_okay = 1

    # Finalizar
    if tarea == "236" and user_okay == 1:
        async = Proceso.objects.filter(id=proceso.id).update(
            estado=tarea, titulo="FINALIZAR PROCESO")
        historia = Historia.objects.create(usuario=str(usuarios.nombres) + " " + str(
            usuarios.apellidos), titulo='FINALIZAR PROCESO', proceso=proceso.id)
        messages.add_message(
            request, messages.INFO, 'Proceso Finalizado con id:'+str(proceso.id))
        return redirect('/procesos')

    # Rechazar
    if tarea == "237" and user_okay == 1:
        async = Proceso.objects.filter(id=proceso.id).update(
            estado=tarea, titulo="RECHAZAR PROCESO")
        historia = Historia.objects.create(usuario=str(usuarios.nombres) + " " + str(
            usuarios.apellidos), titulo='RECHAZAR PROCESO', proceso=proceso.id)
        messages.add_message(
            request, messages.INFO, 'Proceso Rechazado con id:'+str(proceso.id))
        return redirect('/procesos')

    # Pausar
    if tarea == "253" and user_okay == 1 and proceso.estado != "254":
        async = Proceso.objects.filter(id=proceso.id).update(
            estado_pausado=proceso.estado, estado=tarea, titulo="SUSPENSION PROCESO", titulo_pausado=proceso.titulo)
        historia = Historia.objects.create(usuario=str(usuarios.nombres) + " " + str(
            usuarios.apellidos), titulo='SUSPENSION PROCESO', proceso=proceso.id)
        messages.add_message(
            request, messages.INFO, 'Proceso Pausado con id:'+str(proceso.id))
        return redirect('/procesos')

    # Reactivar
    if tarea == "254" and user_okay == 1 and proceso.estado == "1000":
        async = Proceso.objects.filter(id=proceso.id).update(
            estado=tarea, titulo="REACTIVACION PROCESO")
        historia = Historia.objects.create(usuario=str(usuarios.nombres) + " " + str(
            usuarios.apellidos), titulo='REACTIVACION PROCESO', proceso=proceso.id)
        messages.add_message(
            request, messages.INFO, 'Proceso Reactivado con id:'+str(proceso.id))
        return redirect('/procesos')

    return redirect('/procesos')


@login_required
def procesos(request):
    # try:
    usuario = Usuarios.objects.get(user__id=request.user.id)
    procesos2 = Proceso.objects.filter(cerrado="No", rol=usuario.rol)
    procesos3 = Proceso.objects.filter(
        cerrado="No", usuario=str(usuario.user.id))
    procesos = procesos2 | procesos3
    if request.user.is_superuser:
        procesos = procesos | Proceso.objects.filter(cerrado="No")
    procesos.exclude(estado=0)
    # except:
    #    procesos = None
    return render(request, 'procesos.html', {'procesos': procesos})


@login_required
def avisos(request):
    usuario = Usuarios.objects.get(user__id=request.user.id)
    avisos2 = Aviso.objects.filter(visto="no", rol=usuario.rol)
    print(usuario.rol)
    avisos3 = Aviso.objects.filter(
        visto="no", usuario=usuario.user.id)
    avisos = avisos2 | avisos3
    if request.user.is_superuser:
        avisos = Aviso.objects.filter(visto="no")
    avisos_leidos2 = Aviso.objects.filter(visto="si", rol=usuario.rol)
    avisos_leidos3 = Aviso.objects.filter(
        visto="si", usuario=usuario.user.id)
    avisos_leidos = avisos_leidos2 | avisos_leidos3
    if request.user.is_superuser:
        avisos_leidos = Aviso.objects.filter(visto="si")
    print(avisos)

    return render(request, 'avisos.html', {'avisos': avisos, 'avisos_leidos': avisos_leidos})

import locale


@login_required
def reportes(request):
    usuario = Usuarios.objects.get(user__id=request.user.id)

    meses1 = {}
    meses2 = {}
    estados = {}
    rendimiento = []
    rendimiento.append(['Fecha', 'Solicitudes', 'Finalizadas'])

    densidad = []
    densidad.append(['Tarea', 'Cantidad'])

    procesos = Proceso.objects.all()
    locale.setlocale(locale.LC_TIME, "es_ES")
    for proceso in procesos:
        meses1[proceso.created_at.month] = Proceso.objects.filter(
            created_at__month=proceso.created_at.month, cerrado="No").count()
        meses2[proceso.created_at.month] = Proceso.objects.filter(
            created_at__month=proceso.created_at.month, cerrado="Si").count()
        if not [str(proceso.created_at.strftime('%B')), meses1[
                proceso.created_at.month], meses2[proceso.created_at.month]] in rendimiento:
            rendimiento.append([str(proceso.created_at.strftime('%B')), meses1[
                proceso.created_at.month], meses2[proceso.created_at.month]])

        estados[proceso.estado] = Proceso.objects.filter(
            estado=proceso.estado).count()
        estado = titulo[int(proceso.estado)][1]
        if not ["nº"+proceso.estado+" "+estado, estados[proceso.estado]] in densidad:
            densidad.append(
                ["nº"+proceso.estado+" "+estado, estados[proceso.estado]])
    if procesos.count() < 1:
        densidad.append(['No hay tareas', 0])
        rendimiento.append(['No hay Solicitudes', 0])

    autos_obj = Cont_autos.objects.all()
    autos = []
    autos.append(['Fecha', 'Cantidad'])
    autos_num = {}
    if autos_obj.count() < 1:
        autos.append(['No hay autos', 0])
    for a in autos_obj:
        print (a)
        autos_num[a.created_at.strftime('%B')] = Cont_autos.objects.filter(
            created_at__month=proceso.created_at.month).count()
        print (autos_num[a.created_at.strftime('%B')])
        if not [str(a.created_at.strftime('%B')), autos_num[a.created_at.strftime('%B')]] in autos:
            autos.append(
                [str(a.created_at.strftime('%B')), autos_num[a.created_at.strftime('%B')]])
        print(autos)
    return render(request, 'reportes.html', {'rendimiento': rendimiento, 'densidad': densidad, 'autos': autos})



@login_required
def tarea(request, id):

    user = User.objects.get(id=request.user.id)
    usuarios = Usuarios.objects.get(user=user)
    proceso = Proceso.objects.get(id=id)
    titulo = proceso.titulo
    estado = proceso.estado
    rol = proceso.rol
    usuario = proceso.usuario
    okay = 1
    if not rol == "":
        if rol == usuarios.rol:
            okay = 1
    if not usuario == "":
        if str(usuario) == str(usuarios.user.id):
            okay = 1
    if request.user.is_superuser:
        okay = 1
    form = None

    if okay > 0:

        if request.user.is_superuser or proceso.rol == 'radicador' or proceso.usuario == '':
            user_okay = True
        if estado == '236':
            obj = get_object_or_404(Proceso, id=id)
            form = Form236(request.POST or None,
                           request.FILES or None, instance=obj)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    historia = Historia.objects.create(usuario=str(
                        usuarios.nombres) + " " + str(usuarios.apellidos), titulo='FINALIZAR PROCESO', proceso=proceso.id)
                    proceso2 = Proceso.objects.filter(id=proceso.id)
                    proceso2 = Proceso.objects.filter(id=id)
                    proceso2.update(
                        estado='0')
                    messages.add_message(
                        request, messages.INFO, 'Tarea realizada del proceso, id:'+str(proceso.id))
                    count = Cont_autos.objects.create(
                        user=request.user, proceso=id)
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha finalizado el proceso numero:'+str(proceso.id), usuario='4', rol='4')
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha finalizado el proceso numero:'+str(proceso.id), usuario='6', rol='6')
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha finalizado el proceso numero:'+str(proceso.id), usuario='Abogado', rol='Abogado')
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha finalizado el proceso numero:'+str(proceso.id), usuario='secretaria', rol='secretaria')
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha finalizado el proceso numero:'+str(proceso.id), usuario='subdirector', rol='subdirector')
                    proceso2.update(
                        titulo='Finalizado', rol='secretaria', usuario='')
                    opciones(id)
                    return redirect('/')

        if estado == '253':
            obj = get_object_or_404(Proceso, id=id)
            form = Form253(request.POST or None,
                           request.FILES or None, instance=obj)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    historia = Historia.objects.create(usuario=str(
                        usuarios.nombres) + " " + str(usuarios.apellidos), titulo='SUSPENSION PROCESO', proceso=proceso.id)
                    proceso2 = Proceso.objects.filter(id=proceso.id)
                    proceso2 = Proceso.objects.filter(id=id)
                    proceso2.update(
                        estado=1000, titulo="Pausado")
                    messages.add_message(
                        request, messages.INFO, 'Proceso Pausado:, id:'+str(proceso.id))
                    count = Cont_autos.objects.create(
                        user=request.user, proceso=id)
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha suspendido el proceso numero:'+str(proceso.id), usuario='4', rol='4')
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha suspendido el proceso numero:'+str(proceso.id), usuario='6', rol='6')
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha suspendido el proceso numero:'+str(proceso.id), usuario='Abogado', rol='Abogado')
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha suspendido el proceso numero:'+str(proceso.id), usuario='secretaria', rol='secretaria')
                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha suspendido el proceso numero:'+str(proceso.id), usuario='subdirector', rol='subdirector')
                    proceso2.update(rol='secretaria', usuario='')
                    opciones(id)
                    return redirect('/')
        if estado == '254':
            obj = get_object_or_404(Proceso, id=id)
            form = Form254(request.POST or None,
                           request.FILES or None, instance=obj)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    historia = Historia.objects.create(usuario=str(
                        usuarios.nombres) + " " + str(usuarios.apellidos), titulo='REACTIVACION PROCESO', proceso=proceso.id)
                    proceso2 = Proceso.objects.filter(id=proceso.id)
                    proceso2 = Proceso.objects.filter(id=id)
                    proceso2.update(
                        estado=proceso.estado_pausado, titulo=proceso.titulo_pausado)
                    messages.add_message(
                        request, messages.INFO, 'Proceso Reactivado:, id:'+str(proceso.id))

                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha reactivado el proceso numero:'+str(proceso.id), usuario='4', rol='4')

                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha reactivado el proceso numero:'+str(proceso.id), usuario='6', rol='6')

                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha reactivado el proceso numero:'+str(proceso.id), usuario='Abogado', rol='Abogado')

                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha reactivado el proceso numero:'+str(proceso.id) ,usuario='secretaria', rol='secretaria')

                    aviso = Aviso.objects.create(proceso=id,
                                                 user=request.user, titulo='Hay novedades en el proceso,'+str(proceso.id), mensaje='Se ha reactivado el proceso numero:'+str(proceso.id) ,usuario='subdirector', rol='subdirector')
                    # proceso_pausado, usuario_pausado
                    proceso2.update(rol='secretaria', usuario='')
                    opciones(id)
                    return redirect('/')


"""

        models = """


# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pandas as pd
from pandas.tseries.offsets import BDay


class Cont_autos(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    proceso = models.CharField(max_length=200, default="", null=True)

    def __str__(self):
        return str(self.id)


class Historia(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    proceso = models.CharField(max_length=200, default="", null=True)
    titulo = models.CharField(max_length=200, default="", null=True)
    usuario = models.CharField(max_length=200, default="", null=True)

    def __str__(self):
        return str(self.id)


class Usuarios(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    nombres = models.CharField(
        max_length=200, verbose_name='Nombres', default="", null=True)
    apellidos = models.CharField(
        max_length=200,  verbose_name='Apellidos', default="", null=True)
    Rol = (('radicador', 'radicador'),
           ('secretaria', 'secretaria'), ('subdirector', 'subdirector'), ('abogado', 'abogado'), ('ciudadano', 'ciudadano'), )
    rol = models.CharField(
        choices=Rol, verbose_name='Rol', default="ciudadano", blank=True, max_length=200, null=True)
    Tipo_de_documento = (('CC', 'CC'), ('CE', 'CE'), ('NIT', 'NIT'), )
    tipo_de_documento = models.CharField(
        choices=Tipo_de_documento, verbose_name='Tipo de documento', blank=True, max_length=200, null=True)
    numero_documento = models.CharField(unique=True,
                                        max_length=200, verbose_name='Número de documento', default="", null=True)

    direccion = models.CharField(
        verbose_name="Dirección", max_length=200, default="", null=True)
    telefono = models.CharField(
        verbose_name="Telefono", max_length=200, default="", null=True)
    email = models.CharField(unique=True,
                             verbose_name="E-mail", max_length=200, default="", null=True)

    def __str__(self):
        try:
            return self.user.username
        except:
            return "usuarios"


class Opciones(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    proceso = models.CharField(max_length=200, default="", null=True)
    estado = models.CharField(max_length=200, default="", null=True)

    def __str__(self):
        return str(self.id)


class Titulo(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    titulo = models.CharField(max_length=200, default="", null=True)
    estado = models.CharField(max_length=200, default="", null=True)

    def __str__(self):
        return str(self.id)


class Entrada(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    proceso = models.CharField(max_length=200, default="", null=True)
    archivo = models.FileField(
        upload_to='entrada', verbose_name=u'"Anexo"', blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Salida(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Aviso(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    proceso = models.CharField(max_length=200, default="", null=True)
    usuario = models.CharField(max_length=200, default="", null=True)
    rol = models.CharField(max_length=200, default="", null=True)
    titulo = models.CharField(max_length=200, default="", null=True)
    visto = models.CharField(max_length=200, default="no", null=True)
    mensaje = models.TextField(max_length=200, default="", null=True)

    def __str__(self):
        return str(self.id)


class Imprimir(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    proceso = models.CharField(max_length=200, default="", null=True)
    usuario = models.CharField(max_length=200, default="", null=True)
    rol = models.CharField(max_length=200, default="", null=True)
    titulo = models.CharField(max_length=200, default="", null=True)
    titulo_pantalla = models.CharField(max_length=200, default="", null=True)
    pantalla = models.CharField(max_length=200, default="", null=True)
    orden = models.CharField(max_length=200, default="", null=True)
    visto = models.CharField(max_length=200, default="no", null=True)
    mensaje = models.TextField(max_length=200, default="", null=True)

    def __str__(self):
        return str(self.id)
        
class Proceso(models.Model):
    now = timezone.now()
    user = models.ForeignKey(User, blank=True, null=True)
    cerrado = models.CharField(max_length=200, default="No", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pantalla = models.CharField(
        default="INGRESA DATOS DE LA SOLICITUD", max_length=200, null=True)
    estado = models.CharField(default="1", max_length=200, null=True)
    estado_pausado = models.CharField(default="1", max_length=200, null=True)
    estado_reactivado = models.CharField(
        default="1", max_length=200, null=True)
    titulo_pausado = models.CharField(default="1", max_length=200, null=True)
    titulo = models.CharField(
        default="Ingresar Solicitud Radicación", max_length=200, null=True)
    usuario = models.CharField(
        max_length=200, default="", null=True, blank=True)
    rol = models.CharField(max_length=200, null=True, default="radicador")

    def __str__(self):
        return str(self.id)



"""

        forms = """

from django.forms import ModelForm
from principal.models import Proceso, Entrada
from django.db import models
from django import forms
from .models import Usuarios
import random


def ran():
    return str(random.randint(1, 100000))

class EntradaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EntradaForm, self).__init__(
            *args, **kwargs)
    
        for key in self.fields:
            self.fields[key].required = True

    class Meta:
        model = Entrada
        fields = ['archivo']

class usuariosForm(ModelForm):

    # def __init__(self, *args, **kwargs):
    #    super(usuariosForm, self).__init__(
    #        *args, **kwargs)
    #
    #    for key in self.fields:
    #        self.fields[key].required = True

    password = forms.CharField(initial=ran)

    class Meta:
        model = Usuarios
        fields = ['nombres',  'apellidos',
                  'tipo_de_documento', 'numero_documento', 'direccion', 'telefono', 'email', 'rol'

                  

"""
        f1.write(views)
        f2.write(forms)
        f3.write(models)
        nombre = "Ingresar Solicitud de Radicación"
        zero = 0
        automatico = ""
        form_date = ""
        mutex = 0
        opcion = """
def opciones(id):
    proceso = Proceso.objects.get(id=id)
    try:
        opciones = Opciones.objects.get(proceso=id, estado='1')
    except:
        opciones = Opciones.objects.create(proceso=id, estado='1')
    """

        # for i in range(row):
        titulo = []
        titulo.append([])
        titulo[0].append(['0', 'FIN', ''])
        archivo = []
        orden = 0
        titulo_pantalla = ""
        for i in range(row):
            ran = str(random.randint(1, 100))+str(random.randint(1, 100))
            print (i)
            d = worksheet[i][3].strip('?')
            b = worksheet[i][1].strip('?')
            c = worksheet[i][2].strip('?')
            d = worksheet[i][3].strip('?')
            e = worksheet[i][4].strip('?')
            f = worksheet[i][5]
            d2 = ""
            f = str(f)
            c2 = c.replace(' ', '').strip(':').replace('á', 'a').replace('ó', 'o').strip('.').replace(
                '?', '').replace('é', 'e').strip("/").replace('?', '').replace('.', '').replace('-', '')
            espacio = "    "
            if "Demandante" in c or "Demandado" in c or "Tipo de proceso" in c:
                c3 = c2
            else:
                c3 = c2 + ran
            c4 = espacio+c3

            aviso = ""
            if "pantalla" in b:
                titulo.append([])
                titulo.append([])
                titulo.append([])
                titulo[int(d)].append(d)
                titulo[int(d)].append(c)
                titulo[int(d)].append(e)
                titulo_pantalla = c.replace("_", " ")

                # Titulo.objects.create(estado=d, titulo=c)
                pantalla = c2
                pantalla_num = d
                cron = False
            if "Cron.day" in b:
                cron = True

            if "aviso" in b and cron is False:
                
                try:
                    index[d.index("proceso.id")+1]
                    mensaje = d.replace("proceso.id", "'+str(proceso.id)+'")
                except:
                    mensaje = d.replace("proceso.id", "'+str(proceso.id)")
                if "con fecha ejecutoria:" in d:
                    mensaje = mensaje.replace("con fecha ejecutoria:","+' con fecha ejecutoria: '+str(Proceso.objects.get(id=id).f")
                    mensaje = mensaje.replace("(id=id).f ","(id=id).f")
                if "proceso.id" in c:
                    try:
                        index[c.index(")")+1]
                        titulo2 = c.replace("proceso.id", "'+str(proceso.id)+'")
                    except:
                        titulo2 = c.replace("proceso.id", "'+str(proceso.id)")
                if "con fecha ejecutoria:" in d:
                    mensaje = mensaje+")"
                aviso = """
                    aviso = Aviso.objects.create(proceso=id,
                        user=request.user, titulo='"""+titulo2+""", mensaje='"""+mensaje+""", usuario='"""+e+"""', rol='"""+e+"""')
                """

                # print aviso
                f1.write(aviso)
            if "imprimir" in b:
                mensaje = d
                entrada = ""

                if "proceso.id" in mensaje:
                    mensaje = "id"
                else:
                    if "p" in mensaje:
                        mensaje = "Proceso.objects.get(id=id).f"+mensaje
                    else:
                        if mensaje == "":
                            mensaje = "''"
                        else:
                            if "proceso.id" in mensaje:
                                mensaje = id
                            else:
                                mensaje = "Proceso.objects.get(id=id).f"+mensaje
                if "entrada.id" in d:
                    mensaje = "Entrada.objects.filter(proceso=id).order_by('-id')[0]"   
                if "Nombres solicitante" in c:
                    p ='[p.nombres + " " + p.apellidos for p in Proceso.objects.get(id=id).f2.all()]'
                    mensaje = p             
                imprimir = """
                    Imprimir.objects.create(user=request.user, proceso=id, titulo='"""+str(c)+"""', mensaje="""+str(mensaje)+""", orden='"""+str(orden)+"""', pantalla='"""+str(pantalla_num)+"""', titulo_pantalla='"""+str(titulo_pantalla)+"""' )
                """
                
                orden = orden + 1
                f1.write(imprimir)
            if "Select:Usuarios, limit_choices_to={'rol': 'abogado'}" in d:
                # pass
                ran = ""

            if "pantalla" in b:
                mutex = 0
                forms = """


class Form"""+d+"""(ModelForm):

    def __init__(self, *args, **kwargs):
        super(Form"""+d+""", self).__init__(
            *args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

    class Meta:
        model = Proceso
        fields = ["""
                f2.write(forms)
                f1.write("\n")
                contenido = ""
                usu = ""
                estado_redirect = ""
                if "estado" in b:
                    estado_redirect = """
                
                    """
                if "donde" == "donde":  # de momento
                    donde = str(int(d)+1)

                if zero == 0:
                    if "Abogado" in d:
                        usu = "Proceso.objects.get(id=id).usuario"

                    contenido = """
        if request.user.is_superuser or proceso.rol == '"""+e+"""' or proceso.usuario == '"""+usu+"""':
            user_okay = True
        if estado == '"""+d+"""' and user_okay:
            obj = get_object_or_404(Proceso, id=id)
            form = Form"""+d+"""(request.POST or None,
                                                      request.FILES or None, instance=obj)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    historia = Historia.objects.create(usuario=str(usuarios.nombres)+ " "+ str(usuarios.apellidos),titulo='"""+c+"""', proceso=proceso.id)
                    print (proceso)
                    proceso2 = Proceso.objects.filter(id=proceso.id)
                    print (proceso2[0].estado)
                    proceso2 = Proceso.objects.filter(id=id)
                    proceso2.update(
                        estado='"""+donde+"""', )
                    print (proceso2[0].estado)
                    messages.add_message(
                        request, messages.INFO, 'Tarea realizada del proceso, id:'+str(proceso.id))

                    """
                else:
                    if "Abogado" in d:
                        usu = "proceso.usuario"

                    contenido = """
                    proceso2.update(
                        titulo='"""+c+"""', rol='"""+e+"""', usuario='"""+usu+"""' )
                    print (proceso2[0].estado)
                    opciones(id)
                    return redirect('/')

        if estado == '"""+d+"""':
            obj = get_object_or_404(Proceso, id=id)
            form = Form"""+d+"""(request.POST or None,
                                                      request.FILES or None, instance=obj)
            if request.method == 'POST':
                if form.is_valid():
                    form.save()
                    historia = Historia.objects.create(usuario=str(usuarios.nombres)+ " "+ str(usuarios.apellidos),titulo='"""+c+"""', proceso=proceso.id)
                    print (proceso)
                    proceso2 = Proceso.objects.filter(id=proceso.id)
                    print (proceso2[0].estado)
                    proceso2 = Proceso.objects.filter(id=id)
                    proceso2.update(
                        estado='"""+donde+"""', )
                    print (proceso2[0].estado)
                    messages.add_message(
                        request, messages.INFO, 'Tarea realizada del proceso, id:'+str(proceso.id))
                    """

                f1.write(contenido+"\n")
                nombre = c
                zero = zero + 1
            # if "opcion 1" in b:

            fields = []
            fields2 = []
            espacio = "    "
            if "formulario" in b:
                if "Choices:" in d:
                    d = d.replace('Choices:', '')
                    # comma = espacio + c2.upper()+"=('"+d.encode('utf-8')+"')"
                    lista = d.split(",")
                    tupla = [(i, i) for i in lista]
                    f3.write(
                        c4.upper()+"=" +
                        str(tuple(tupla)).replace(
                            "Rechazad", "Rechazado"))
                    f3.write('\n')
                    f3.write(
                        espacio+"f"+f + "=" + "models.CharField(choices="+c4.upper()+",verbose_name='"+c+"',blank=True, max_length=200, null=True)")
                    f3.write('\n')

                if "Select" in d:
                    d = d.replace('Select', '').replace(
                        ':', '').replace('á', 'a').replace('ó', 'o').replace('.', '').replace('?', '').replace('é', 'e').replace("/", '')

                    if "Abogado" in d:
                        # ran = ""
                        d = "Usuarios , limit_choices_to={'rol': 'abogado'}}, "
                    if "Abogado" in c:
                        esp = "    "
                    else:
                        esp = ""
                    cmd = espacio + "f"+f+"=" + \
                        "models.ForeignKey("+d+"},verbose_name=' "+c + \
                        "  ', blank=True, null=True, related_name='f"+f+"'  )"

                    cmd = cmd.replace('}}', '}').replace(
                        ', ,', ',').replace('}, }', '},').replace(',,', ',')
                    print (cmd)
                    cmd = cmd.replace(
                        "{'rol' 'abogado'}", "{'rol' :'abogado'}")
                    f3.write(cmd)
                if "Multiple" in d:
                    d = d.strip('Multiple:')
                    f3.write(espacio+"f"+f+"=" + "models.ManyToManyField("+d +
                             ",verbose_name=' "+c+"  ', blank=True,related_name='f"+f+"')")
                if "Date" in d:
                    if ":" in d:
                        default = d[d.index(":")+1:]
                        d = d[:d.index(":")+1]
                    else:
                        default = "now"
                    f3.write(
                        espacio+"f"+f+"=" + "models.DateField(verbose_name='"+c+"', default=now, blank=True, null=True)")
                    if not "automatico" in e:
                        form_date +=  """
    """+c4 + """ = forms.DateInput.input_type = 'date' """
                    else:
                        automatico += """
            self.f"""+f+""" = """+default
                if "File" in d:
                    #archivo.append("f"+f, "p"+pantalla)

                    f1.write("""
                    count = Cont_autos.objects.create(user=request.user, proceso=id)
                        """)

                    f3.write("""
""" +
                             espacio+"f"+f+"=" + "models.FileField(upload_to='procesos/%Y/%m/%d',verbose_name='"+c+"', blank=True, null=True)")

                if "Varchar" in d:
                    f3.write(espacio+"f"+f+"=" + "models.CharField(max_length=200, verbose_name='" +
                             c2+"', blank=True, null=True)")
                if "Int" in d:
                    f3.write(espacio+"f"+f+"=" + "models.IntegerField(verbose_name='" +
                             c2.replace('_', ' ')+"', default=0, blank=True, null=True)")
                if not "automatico" in e:
                    f2.write("'f"+f+"',")

            if "estado" in b and c != "1" and mutex < 1:
                mutex = 1
                f2.write("]")
                f2.write(form_date)
                form_date = ""

            if "pantalla" in b:
                mutex = 0
            f3.write('\n')

            j = j+1
            if "opcion" in b:
                if "Corregir" in c:
                    de = str("\'Corregir\'")
                else:
                    de = """titulo["""+str(int(d))+"""][1]"""
                condicion = """if proceso.f""" + \
                    c[:c.index("==")]+""" == '"""+c[c.index("==")+2:]+"""'"""
                if "Medida Cautelar Autónoma" in c:
                    condicion = """if proceso.f""" + \
                        c[:c.index(
                            "==")]+""" ==  'Acepta' and proceso.f1 == 'Medida Cautelar Autónoma'"""
                if "Proceso Declarativo Verbal" in c:
                    condicion = """if proceso.f""" + \
                        c[:c.index(
                            "==")]+""" ==  'Acepta' and proceso.f1 == 'Proceso Declarativo Verbal'"""
                if "Proceso Declarativo Verbal Sumario" in c:
                    condicion = """if proceso.f""" +\
                        c[:c.index(
                            "==")]+""" ==  'Acepta' and proceso.f1 == 'Proceso Declarativo Verbal Sumario'"""
                if "Prueba Extraprocesal" in c:
                    condicion = """if proceso.f""" +\
                        c[:c.index(
                            "==")]+""" ==  'Acepta' and proceso.f1 == 'Prueba Extraprocesal'"""
                if "estado" in b:
                    if "0" in d:
                        d = 0
                opcion = opcion + """
    """+condicion+""":
        Proceso.objects.filter(id=id).update( f"""+c[:c.index("==")]+"""=None,
            estado="""+d+""", titulo="""+de+""", rol=titulo["""+str(int(d))+"""][2], usuario=titulo["""+str(int(d))+"""][2] )

    """

        f1.write("""        
    return render_to_response(
        'tarea_detalle.html', {
            'form': form, 'titulo': titulo, 'proceso': proceso},
        context_instance=RequestContext(request)
    )""")
        f3.write("""


    def save2(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        if self.created_at:
            """ + automatico +
                 """
        self.updated_at = timezone.now()
        return super(Proceso, self).save(*args, **kwargs)



        """)

        f1.write(opcion)
        f1.write("""

titulo = """+str(titulo).replace('[[[', '[[').replace(']],', '],') + """

            """)
        f1.write("""


if __name__ == '__tarea__':
    tarea()
            """)
        f4.write(str(tuple(archivo)))
        f4.close()
        f1.close()
        f2.close()
        f3.close()
