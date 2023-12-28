from django.urls import path
from .views import (
			inicio,
			jugar,
			sinTiempo,
			tablero,
			sinTiempo,
			resultado,
			resultado1,
			resultado2,
			comentario,
            tutor)

urlpatterns = [
	
	path('', inicio, name='inicio'),
	path('tablero/', tablero, name='tablero'),
	path('jugar/<int:inter>/', jugar, name='jugar'),  # Define la URL para capturar el parámetro 'inter' como un entero
	path('sinTiempo/', sinTiempo, name='sinTiempo'),
    path('resultado/<int:pregunta_respondida_pk>', resultado, name='resultado'),
    path('resultado1/<int:pregunta_respondida_pk>', resultado1, name='resultado1'),
    path('resultado2/<int:pregunta_respondida_pk>', resultado2, name='resultado2'),
	path('comentario/', comentario, name='comentario'),
	path('sinTiempo/', sinTiempo, name='sinTiempo'),
    path('tutor/',tutor, name='tutor')

]