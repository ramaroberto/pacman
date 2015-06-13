from RLObjects import Posicion, Accion, Estado
import random


_epsilon = 0.1


def GetSiguienteAccionGreedy(estado, Q):
    
    # Tomo todos los valores de Q para el estado pasado por parametro
    Q_estado = [(b, Q.activate([estado.angulo, estado.velocidadAngular, estado.posicion, b])) for b in range(Accion.maxValor + 1) ]

    # Me quedo con la accion que minimiza Q_estado
    accionMin, valorMin = Q_estado[0]
    
    for (acc, valor) in Q_estado:
        if (valor < valorMin):
            accionMin = acc
            valorMin = valor

    #lEstado = [a for (a,v) in Q_estado if v == valorMin]

    return accionMin
    #return lEstado[random.randint(0,len(lEstado)-1)]



def GetSiguienteAccionEpsilonGreedy(estado, Q):
    
    # Elijo siguiente accion de manera aleatoria con probabilidad
    # epsilon, y de manera greedy con probabilidad (1 - epsilon)
    # (la funcion de valor contine costos, no rewards, por lo tanto se minimiza)
    rndNumber = random.random()

    if rndNumber <= _epsilon:
        accion = random.randint(0, Accion.maxValor)
    else:
        accion = GetSiguienteAccionGreedy(estado, Q)

    return accion



def GetSiguienteAccionRandom(estado):

    accion = random.randint(0, Accion.maxValor)
    return accion




