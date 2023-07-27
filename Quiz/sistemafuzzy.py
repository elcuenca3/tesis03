from simpful import *

difSig = 0

def sistemaFuzzy(calificacion, tiempo, ayuda, dificultad):
	global difSig
	if ayuda == False:
		ayuda = 0
	else:
		ayuda = 1
	
	FS = FuzzySystem()

	# Define fuzzy sets and linguistic variables
	# Calificacion
	C_1 = FuzzySet(function=Triangular_MF(a=0, b=0, c=1), term="incorrecto")
	C_2 = FuzzySet(function=Triangular_MF(a=0, b=1, c=1), term="correcto")
	FS.add_linguistic_variable("calificacion", LinguisticVariable([C_1, C_2], concept="Calificacion", universe_of_discourse=[0,1]))

	# Tiempo
	T_1 = FuzzySet(function=Trapezoidal_MF(a=0, b=0, c=50, d=60), term="poco")
	T_2 = FuzzySet(function=Trapezoidal_MF(a=60, b=65, c=70, d=75), term="medio")
	T_3 = FuzzySet(function=Trapezoidal_MF(a=75, b=80, c=90, d=90), term="mucho")
	FS.add_linguistic_variable("tiempo", LinguisticVariable([T_1, T_2, T_3], concept="Tiempo por pregunta", universe_of_discourse=[0,90]))

	# Ayuda
	A_1 = FuzzySet(function=Triangular_MF(a=0, b=0, c=1), term="no")
	A_2 = FuzzySet(function=Triangular_MF(a=0, b=1, c=1), term="si")
	FS.add_linguistic_variable("ayudas", LinguisticVariable([A_1, A_2], concept="Utilizo ayuda", universe_of_discourse=[0,1]))

	# Define output fuzzy sets and linguistic variable
	# Dificultad sube o baja
	D_1 = FuzzySet(function=Triangular_MF(a=0, b=0, c=0.5), term="baja")
	D_2 = FuzzySet(function=Triangular_MF(a=0.5, b=1, c=1), term="suba")
	FS.add_linguistic_variable("dificultadSig", LinguisticVariable([D_1, D_2], universe_of_discourse=[0,1]))

	# Define fuzzy rules
	R1 = "IF (calificacion IS incorrecto) OR (tiempo IS mucho) OR (ayudas IS si) THEN (dificultadSig IS baja)"
	R2 = "IF (calificacion IS correcto) AND (tiempo IS medio) AND (ayudas IS no) THEN (dificultadSig IS sube)"
	R3 = "IF (calificacion IS correcto) AND (tiempo IS poco) AND (ayudas IS no) THEN (dificultadSig IS sube)"
	FS.add_rules([R1, R2, R3])

	# Set antecedents values
	FS.set_variable("calificacion", calificacion) 
	FS.set_variable("tiempo", tiempo)
	FS.set_variable("ayudas", ayuda)

	dificultadSig = FS.inference(['dificultadSig'])

	difSig = dificultadSig.get('dificultadSig')

	definir_dificultad(difSig, dificultad)

def definir_dificultad(dif, dificultad):
	global difSig
	if dif <= 0.5:
		difSig = dificultad-1

	if difSig < 1:
		difSig = 1

	if dif > 0.5:
		difSig = dificultad+1

	if difSig > 3:
		difSig = 3

def obtener_dif_pregunta():
	global difSig
	return difSig