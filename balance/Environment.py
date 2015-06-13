from RLObjects import Posicion, Accion, Estado
import math


targetValue = 0.2
penalizacion = 0.04             # Costo mayor

def Costo(estado):

    # Penalizo los bordes
    if (estado.posicion == Posicion.BORDE_DERECHO or estado.posicion == Posicion.BORDE_IZQUIERDO):
        return penalizacion


    # Chequeo que no este pasando por el target muy rapido
    # En ese caso lo penalizo
    if abs(estado.velocidadAngular) >= 8:
		return penalizacion

    
    # Estado objetivo
    if (abs(estado.angulo) <= targetValue):
		return 0


    # Cuanto mas cerca del cero menos costo
    costo = ( abs(float(estado.angulo) / 100.0) )

    return costo
