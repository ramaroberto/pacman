from RLObjects import Posicion, Accion, Estado
from Simulator import Simulator
#from ODESim import ODESim

_simulador = Simulator(True, True)


def Inicializar(imprimirAngulo, imprimirTiempo):
    global _simulador
    _simulador = Simulator(imprimirAngulo, imprimirTiempo)
    #_simulador = ODESim()


def setAnguloInicial(angulo):
    _simulador.cartPole_angulo = angulo


def EjecutarAccion(accion):

    
    if (accion == Accion.DERECHA):
        accSim = 1
    elif (accion == Accion.IZQUIERDA):
        accSim = -1
    else:
        accSim = 0

    # Corro las veces necesarias para mostrar el resultado
    for i in range(_simulador.vueltasPorMovimiento):
        _simulador.run(accSim)


def GetEstado():
    result = Estado()

    result.angulo = _simulador.cartPole_angulo
    result.velocidadAngular = int(_simulador.cartPole_velocidadAngular)


    # Posicion
    if _simulador.cartPole_x <= _simulador.xMin:
        result.posicion = Posicion.BORDE_IZQUIERDO

    elif _simulador.cartPole_x >= _simulador.xMax:
        result.posicion = Posicion.BORDE_DERECHO

    else:
        result.posicion = Posicion.CENTRO

    return result


def GetKeyPressed():
    return _simulador.GetKeyPressed()


def Finalizar():
    _simulador.Finalizar()



