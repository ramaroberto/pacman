import sys, pygame, Experiment, signal
from pygame.locals import *
from RLObjects import Accion

def exit_handler(signal, frame):

    global f
    pygame.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

Experiment.Inicializar(False, True)
mover = False
      
while (True):

    for event in pygame.event.get():
        
        if event.type == KEYUP:
            #mover = False          # Para que no se mueva constantemente
            pass
        
        elif event.type == KEYDOWN:
            #if not hasattr(event, 'key'): continue
        
            if event.key == K_ESCAPE:
                Experiment.Finalizar()

            elif event.key == K_SPACE:      # La barra espaciadora corta el movimiento
                mover = False

            elif event.key == K_RIGHT:
                mover = True
                movimiento = Accion.DERECHA
                
            elif event.key == K_LEFT:
                mover = True
                movimiento = Accion.IZQUIERDA

            
    if mover:
        Experiment.EjecutarAccion(movimiento)
    else:
        Experiment.EjecutarAccion(-25)


##    key = Experiment.GetKeyPressed()
##    
##    if key[pygame.K_RIGHT]:
##        print "derecha"
##        Experiment.EjecutarAccion(Accion.DERECHA)
##            
##    elif key[pygame.K_LEFT]:
##        print "izquierda"
##        Experiment.EjecutarAccion(Accion.IZQUIERDA)
##        
##    else:
##        print key
##        Experiment.EjecutarAccion(-25)


             
