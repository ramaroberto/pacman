import sys, pygame, time, Experiment, signal, ActionFunctions
from pygame.locals import *
from networkreader import NetworkReader
from RLObjects import Accion

def exit_handler(signal, frame):

    global f
    pygame.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)


episodio = 0
lastTime = time.time()
muestrasPorEpisodio = 100
muestrasTomadas = 0
archivoQ = "Q_Aprendizaje/aprendizaje_"
tiempoDeMuestreo = 0.01

Experiment.Inicializar(False, True)

while(True):

    # Para salir: ESC
    for event in pygame.event.get():
        if not hasattr(event, 'key'): continue
        elif event.key == K_ESCAPE: pygame.quit()


    newTime = time.time()

    if (newTime - lastTime > tiempoDeMuestreo):

        # Chequeo si tengo que cambiar de episodio
        if muestrasPorEpisodio == muestrasTomadas:
            episodio = episodio + 1
            muestrasTomadas = 0

            if episodio == 8:
                Experiment.Finalizar()
                sys.exit(0)

            # Reinicio sistema
            pygame.quit()
            Experiment.Inicializar(False, True)
            
            # Levanto nueva Q
            Q = NetworkReader.readFrom(archivoQ + str(episodio) + ".xml")

        
        muestrasTomadas = muestrasTomadas + 1
        estado = Experiment.GetEstado()
        
        if episodio == 0:               # Episodio 0 - Random    
            accion = ActionFunctions.GetSiguienteAccionRandom(estado)
        else:
            accion = ActionFunctions.GetSiguienteAccionGreedy(estado, Q)
        
        Experiment.EjecutarAccion(accion)

        lastTime = newTime
