from email.policy import default
from genericpath import exists
from tabnanny import verbose
from django.db import models
from django.conf import settings


from .sistemafuzzy import obtener_dif_pregunta

import random

# Cambios echos por Erick
# class Materia (models.Model):
# 	quizMateria  =models.ForeignKey(verbose_name="Nombre materia",  null=True)
# 	quizMateria_docente  =models.ForeignKey(verbose_name="Nombre docente",  null=True)
# 	quizCiclo  =models.TextField(verbose_name='Ip usuario')

class Pregunta(models.Model):

	NUMER_DE_RESPUESTAS_PERMITIDAS = 1

	texto = models.TextField(verbose_name='Texto de la pregunta')
	dificultad = models.IntegerField(verbose_name='Dificultad pregunta', null=True)
	max_puntaje = models.DecimalField(verbose_name='Maximo Puntaje', default=3, decimal_places=2, max_digits=6)
	tipo = models.TextField(verbose_name='Tipo de pregunta')
	unidad = models.IntegerField(verbose_name='Unidad a la que pertenece')
	# Cambios echos por Erick
	# materia =models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='nombre de materia', null=False)
	def __str__(self):
		return self.texto


class ElegirRespuesta(models.Model):

	MAXIMO_RESPUESTA = 3
	MINIMO_RESPUESTA = 2

	pregunta = models.ForeignKey(Pregunta, related_name='opciones', on_delete=models.CASCADE)
	correcta = models.BooleanField(verbose_name='¿Es esta la pregunta correcta?', default=False)
	texto = models.TextField(verbose_name='Texto de la respuesta')

	def __str__(self):
		return self.texto

class QuizUsuario(models.Model):
	usuario = models.TextField(verbose_name='Ip usuario')
	nombre = models.TextField(verbose_name='Nombre del usuario', null=True)
	puntaje_total = models.DecimalField(verbose_name='Puntaje Total', null=True, default=0.00, decimal_places=2, max_digits=10)
	num_p = models.IntegerField(verbose_name='Numero de  preguntas respondidas', default=0)

	def crear_intentos(self, pregunta):
		intento = PreguntasRespondidas(pregunta=pregunta, quizUser=self, nombreUser=self)
		intento.save()

	def getNumP(self):
		respondidas = PreguntasRespondidas.objects.filter(quizUser=self).values_list('pregunta__pk', flat=True)
		return len(respondidas) + 1

	def obtener_nuevas_preguntas(self):
		dif = obtener_dif_pregunta()
		print(dif)
		respondidas = PreguntasRespondidas.objects.filter(quizUser=self).values_list('pregunta__pk', flat=True)
		preguntas_restantes = Pregunta.objects.exclude(pk__in=respondidas)
		if len(respondidas) >= 15:
			return None
		try:
			return random.choice(preguntas_restantes.filter(dificultad=dif))
		except IndexError:
			return random.choice(preguntas_restantes)

	def validar_intento(self, pregunta_respondida, respuesta_selecionada, dificultad, ayuda, tiempo):

		if respuesta_selecionada.correcta is True:
			pregunta_respondida.correcta = True
			pregunta_respondida.puntaje_obtenido = respuesta_selecionada.pregunta.max_puntaje
			pregunta_respondida.respuesta = respuesta_selecionada
			pregunta_respondida.dificultad = dificultad
			pregunta_respondida.uso_ayuda = ayuda
			calificacion = 1
			pregunta_respondida.tiempo_pregunta = tiempo

		else:
			pregunta_respondida.respuesta = respuesta_selecionada
			pregunta_respondida.dificultad = dificultad
			pregunta_respondida.uso_ayuda = ayuda
			calificacion = 0
			pregunta_respondida.tiempo_pregunta = tiempo

		self.num_p += 1
		self.save()
		pregunta_respondida.save()

		self.actualizar_puntaje()

		return calificacion

	def actualizar_puntaje(self):
		puntaje_actualizado = self.intentos.filter(correcta=True).aggregate(
			models.Sum('puntaje_obtenido'))['puntaje_obtenido__sum']

		self.puntaje_total = puntaje_actualizado
		self.save()

	def guardar_comentario(self, texto_comentario):
		comentario = ComentarioUsuario(comentario=texto_comentario, quizUser=self, nombreUser=self)
		comentario.save()

class PreguntasRespondidas(models.Model):
	quizUser = models.ForeignKey(QuizUsuario, on_delete=models.CASCADE, related_name='intentos')
	nombreUser = models.ForeignKey(QuizUsuario, on_delete=models.CASCADE, related_name='intentos_username', null=True)
	pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='texto_pregunta')
	respuesta = models.ForeignKey(ElegirRespuesta, on_delete=models.CASCADE, null=True)
	dificultad = models.IntegerField(verbose_name='Dificultad de la pregunta', null=True)
	uso_ayuda = models.BooleanField(verbose_name='¿Utilizo ayuda?', default=False)
	tiempo_pregunta = models.IntegerField(verbose_name='Tiempo que de la pregunta', null=True)
	correcta  = models.BooleanField(verbose_name='¿Es esta la respuesta correcta?', default=False)
	puntaje_obtenido = models.DecimalField(verbose_name='Puntaje Obtenido', default=0, decimal_places=2, max_digits=6)

class ComentarioUsuario(models.Model):
	quizUser = models.ForeignKey(QuizUsuario, on_delete=models.CASCADE, related_name='comentario')
	nombreUser = models.ForeignKey(QuizUsuario, on_delete=models.CASCADE, related_name='comentario_username', null=True)
	comentario = models.TextField(verbose_name='Comentario')

	
	