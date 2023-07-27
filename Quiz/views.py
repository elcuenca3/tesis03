import string
from tkinter.tix import INTEGER
from django.shortcuts import render, redirect, get_object_or_404

from Quiz.sistemafuzzy import sistemaFuzzy

from .forms import RegistroFormulario, UsuarioLoginFormulario

from django.core.exceptions import ValidationError, MultipleObjectsReturned

from .models import QuizUsuario, Pregunta, PreguntasRespondidas, ElegirRespuesta

from django.http import Http404

from django.core.exceptions import ObjectDoesNotExist

array = []
sec = 1800
t_pregunta = 0
ultima = 0
pregunta = None
getP = True
bandera = False
nombre_usuario = ''

def inicio(request):
	global sec
	sec = 1800
	global t_pregunta
	t_pregunta = 0
	global ultima
	ultima = 0
	global pregunta
	pregunta = None
	global getP
	getP = True
	global bandera
	bandera = False
	global array
	array = []
	global nombre_usuario

	nombre_usuario = request.POST.get('nombre_estudiante')

# def index(request):
# 	return render(request, 'inicio.html')

	if request.method =='POST':
		if nombre_usuario != '' and nombre_usuario is not None:
			if len(nombre_usuario) > 10:
				context = {
					'alerta': 'El nombre ingresado tiene más de 10 caracteres.'
				}
				return render(request, 'inicio.html', context)
			try:
				QuizUsuario.objects.get_or_create(usuario=get_client_ip(request), nombre=nombre_usuario)
			except:
				context = {
					'alerta':'Ingrese otro nombre de usuario'
				}
				return render(request, 'inicio.html', context)
			return redirect('jugar')
	return render(request, 'inicio.html')

def tablero(request):
	global nombre_usuario
	try:
		QuizUser = QuizUsuario.objects.get(usuario=get_client_ip(request), nombre=nombre_usuario)
		n_preguntas = QuizUser.num_p
	except:
		n_preguntas = 0

	total_usaurios_quiz = QuizUsuario.objects.order_by('-puntaje_total')[:10]
	contador = total_usaurios_quiz.count()

	context = {
		'user':nombre_usuario,
		'usuario_quiz':total_usaurios_quiz,
		'contar_user':contador
	}

	if n_preguntas >= 15:
		codigo = get_client_ip(request) + '.' + nombre_usuario
		context = {
			'user':nombre_usuario,
			'usuario_quiz':total_usaurios_quiz,
			'contar_user':contador,
			'codigo':'Su código es: ' + codigo
		}

	return render(request, 'play/tablero.html', context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def jugar(request):
	global array
	global sec
	global t_pregunta
	global ultima
	global pregunta
	global getP
	global bandera
	global nombre_usuario

	try:
		QuizUser = QuizUsuario.objects.get(usuario=get_client_ip(request), nombre=nombre_usuario)
	except:
		QuizUser = QuizUsuario.objects.filter(usuario=get_client_ip(request)).last()
		nombre_usuario = QuizUser.nombre

	context = {
			'pregunta':pregunta,
			'n_pregunta': QuizUser.num_p + 1,
			'array':len(array),
			'sec': sec,
		}
	if request.GET.get('bandera', False):
		bandera = True

	if request.method == 'POST':

		pregunta_pk = request.POST.get('pregunta_pk')

		respuesta_pk = request.POST.get('respuesta_pk')

		if respuesta_pk is None:
			return render(request, 'play/jugar.html', context)

		ultima = t_pregunta
		QuizUser.crear_intentos(pregunta)
		pregunta_respondida = QuizUser.intentos.select_related('pregunta').filter(pregunta__pk=pregunta_pk).last()
		print(type(pregunta_respondida))
		opcion_selecionada = pregunta_respondida.pregunta.opciones.get(pk=respuesta_pk)
		array.append(pregunta_respondida)


		dificultad = pregunta.dificultad

		calificacion = QuizUser.validar_intento(pregunta_respondida, opcion_selecionada, dificultad, bandera, ultima)

		sistemaFuzzy(calificacion, ultima, bandera, dificultad)

		getP = True
		bandera = False

		return redirect('resultado', pregunta_respondida.pk)

	else:
		if len(array) <= 15 and getP == True:
			pregunta = QuizUser.obtener_nuevas_preguntas()
			if pregunta is None:
				return render(request, 'play/jugar.html', {'array': 15})

			getP = False
		else:
			context = {
				'n_pregunta': QuizUser.num_p + 1,
				'array':len(array),
				'sec': sec,

			}
	try:
		correcta = obtenerCorrecta(pregunta.id, ElegirRespuesta)
	except AttributeError:
		context = {
			'array':15
		}
		return render(request, 'play/jugar.html', context)
	context = {
				'pregunta':pregunta,
				'n_pregunta': QuizUser.num_p + 1,
				'array':len(array),
				'sec': sec,
				'correcta': correcta,
			}

	sec = request.GET.get('sec', None)

	if sec != None:
		t_pregunta = 1800 - int(sec) - ultima

	return render(request, 'play/jugar.html', context)

def resultado(request, pregunta_respondida_pk):
	respondida = get_object_or_404(PreguntasRespondidas, pk=pregunta_respondida_pk)

	context = {
		'respondida':respondida
	}
	return render(request, 'play/resultado.html', context)

def sinTiempo(request):

	return render(request, 'play/sinTiempo.html')

def comentario(request):

	QuizUser = QuizUsuario.objects.get(usuario=get_client_ip(request), nombre=nombre_usuario)
	coment = request.POST.get('comentario')

	context = {
		'bandera':False
	}

	if request.method == 'POST':
		QuizUser.guardar_comentario(coment)
		context = {
			'bandera':True,
			'gracias':'Gracias por tu comentario'
		}


	return render(request, 'comentario.html', context)

def obtenerCorrecta(pregunta_id, respuesta):
	correcta = respuesta.objects.filter(pregunta=pregunta_id, correcta=True).get()

	return correcta