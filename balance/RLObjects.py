import math

class Accion:
    DERECHA = 1
    IZQUIERDA = 0
    #NADA = 2
    maxValor = 1


class Posicion:
    BORDE_IZQUIERDO = 1
    BORDE_DERECHO = 2
    CENTRO = 3


class Estado:
    angulo = 0
    velocidadAngular = 0
    posicion = Posicion.CENTRO


    def __init__(self):
        self.angulo = math.pi
        self.velocidadAngular = 0
        posicion = 0

    def __repr__(self):
        return "Angulo: {}, Velocidad Angular: {}, Posicion: {})".format(
            self.angulo,
            self.velocidadAngular,
            self.posicion)
        
