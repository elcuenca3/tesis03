from django.urls import path
from .views import (
			inicio,
			jugar,
			sinTiempo,
			tablero,
			sinTiempo,
			resultado,
			comentario)

urlpatterns = [
	
	path('', inicio, name='inicio'),
	path('tablero/', tablero, name='tablero'),
	path('jugar/', jugar, name='jugar'),
	path('sinTiempo/', sinTiempo, name='sinTiempo'),
	path('resultado/<int:pregunta_respondida_pk>', resultado, name='resultado'),
	path('comentario/', comentario, name='comentario'),

]