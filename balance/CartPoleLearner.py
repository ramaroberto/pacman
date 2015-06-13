import sys, time, datetime, random, atexit, pygame, signal
from pygame.locals import *
from sets import Set

from networkwriter import NetworkWriter
from networkreader import NetworkReader

import Experiment
import ActionFunctions
import Environment

from NFQIteration import NFQIteration
from RLObjects import Posicion, Accion, Estado

f = None

def exit_handler(signal, frame):

    global f
    pygame.quit()
    if (f != None): f.close()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)



# -------------
# Configuracion
# -------------


aprender = True                     # Indica si el algoritmo tiene que aprender Q o utilizar la que ya tiene
aprender_QAnterior = False          # Indica si usa archivoQ como Q inicial en la etapa de aprendizaje
imprimirResultados = True           # Imprimir informacion para graficar

archivoQ = "Q/qWeights.xml"         # Archivo xml con la red neuronal aprendida
                                    
tiempoDeMuestreo = 0.01             # Cada cuanto se chequea el estado del sistema
episodios = 1000

muestrasEpisodio0 = 1000            # Cantidad de muestras random que se toman inicialmente
epochsNFQ_Episodio0 = 500           # Cantidad de iteraciones de NFQ en el primer episodio (muestras random)

muestrasPorEpisodio = 200           # Cantidad de muestras que se toman antes de volver a entrenar la red neuronal
epochsNFQ = 1000                     # Cantidad de iteraciones de NFQ en el resto de los episodios



# Contador de tiempo
lastTime = time.time()


# Chequeo si los parametros vinieron por linea de comando
for i in range(1, len(sys.argv)):
	
	if sys.argv[i] == "-a":
		aprender = True;
		
	elif sys.argv[i] == "-v":
		aprender = False;
		
	elif sys.argv[i] == "-q":
		archivoQ = sys.argv[i + 1]
		i = i + 1
		
	elif sys.argv[i] == "-m":
		muestrasPorEpisodio = int(sys.argv[i + 1])
		i = i + 1
		
	elif sys.argv[i] == "-i":
		epochsNFQ = int(sys.argv[i + 1])
		i = i + 1
		
		

# -----------
# Aprendizaje 
# -----------

if aprender:


    # Variables iniciales
    nfq = NFQIteration()            # Algoritmo para entrenar
    muestrasTomadas = 0
    transitionSamples = Set()


    if imprimirResultados:
        f = open("resultados.txt", "w")
        
        f.write("Muestras Episodio 0:" + str(muestrasEpisodio0) + "\n" )
        f.write("Iteraciones NFQ Episodio 0: " + str(epochsNFQ_Episodio0) + "\n")
        f.write("Muestras:" + str(muestrasPorEpisodio) + "\n" )
        f.write("Iteraciones NFQ: " + str(epochsNFQ) + "\n")
        f.write("Iteraciones NFQ, epochs de la RN: " + str(nfq._epochsNN) + "\n\n\n")
        
        f.write("Episodio\t% Muestras Costo 0\tCosto Acumulado\tPromedio Altura \tMaxima Altura\tHora\n")


    if aprender_QAnterior:
        # Levanto Q del archivo correspondiente
        nfq.Q = NetworkReader.readFrom(archivoQ)
        

    # Loop principal    
    for episodio in range(episodios):

        print "Episodio {}".format(episodio)

        #transitionSamples = []


        # Variables para graficar
        hoy = datetime.datetime.now()   # Para imprimir hora de inicio del episodio en txt de resultados 
        angulos = []                    # Angulos a los que llega durante el episodio (para sacar promedio)
        muestrasCostoCero = 0           # Cantidad de muestras que devolvieron costo 0
        alturaMaxima = -1               # Altura maxima alcanzada (angulo minimo en valor absoluto)
        costoAcumulado = 0
            
            
        # Inicializo el sistema con el que trabajo
        Experiment.Inicializar(True, True)
        muestrasTomadas = 0


        # El primer episodio toma mas muestras, corre NFQ mas veces y arranca desde arriba
        if(episodio == 0):
            Experiment.setAnguloInicial(0.01)
            NFQIteration._epochs = epochsNFQ_Episodio0
            muestrasTotales = muestrasEpisodio0
        else:
            NFQIteration._epochs = epochsNFQ
            muestrasTotales = muestrasPorEpisodio

        
        # Estado y acciones iniciales
        estado = Experiment.GetEstado()
        accion = ActionFunctions.GetSiguienteAccionEpsilonGreedy(estado, nfq.Q)
        lastTime = time.time()
        Experiment.EjecutarAccion(accion)

	# Itero hasta obtener una determinada cantidad de muestras
        while muestrasTomadas < muestrasTotales:    


            # Chequeo que haya pasado el tiempo necesario para
            # tomar la siguiente muestra

            newTime = time.time()
    
            if newTime - lastTime > tiempoDeMuestreo:

                # Leo el estado del sistema
                # Se corresponde con el estado sucesor (s')
                # a la accion tomada en la vuelta anterior
                estadoSiguiente = Experiment.GetEstado()

                
                # Guardo datos para graficar (no guardo resultados
                # de las muestras tomadas random)
                if imprimirResultados and episodio > 0:

                    ang = estadoSiguiente.angulo
                    angulos.append(ang)
                    
                    if abs(ang) < alturaMaxima or alturaMaxima == -1:
                        alturaMaxima = float(abs(ang))

                    if  costo == 0:
                        muestrasCostoCero = muestrasCostoCero + 1
                       
                    costoAcumulado = costoAcumulado + costo


                # Guardo la muestra (s, a, s', c)
                # (c = costo de la transicion <s,a,s'>)
                costo = Environment.Costo(estadoSiguiente)
                muestra = (estado, accion, estadoSiguiente, costo)
                transitionSamples.add(muestra)
                muestrasTomadas = muestrasTomadas + 1


                # Datos para la proxima iteracon
                # Calculo la siguiente accion en base al Q actual
                estado = estadoSiguiente

                if episodio < 1:
                    # El primer episodio ejecuta acciones random
                    accion = ActionFunctions.GetSiguienteAccionRandom(estado)  
                else:
                    accion = ActionFunctions.GetSiguienteAccionEpsilonGreedy(estado, nfq.Q)

                # Ejecuto la accion
                Experiment.EjecutarAccion(accion)

                # Reinicio contador de tiempo
                lastTime = newTime

             


        # Si termine de acumular suficiente experiencia actualizo Q
        Experiment.Finalizar()
        nfq.train(transitionSamples)
                
        # Guardo la Q obtenida
        nombreArchivo = "Q/qWeights_" + str(episodio) + ".xml"
        NetworkWriter.writeToFile(nfq.Q, nombreArchivo)

        # Imprimo resultados en el resultados.txt
        if imprimirResultados and episodio > 0:

            absAngulos = [abs(ang) for ang in angulos]
            promedio = (sum(absAngulos)) / float(len(angulos))
            porcentajeCostoCero = float(muestrasCostoCero * 100) / float(muestrasPorEpisodio)
            
            fileLine = str(episodio) + "\t"
            fileLine += str(porcentajeCostoCero) + "\t"
            fileLine += str(costoAcumulado) + "\t"
            fileLine += "{0:3f}\t".format(promedio)
            fileLine += "{0:3f}\t".format(alturaMaxima)
            fileLine += hoy.strftime("%d-%m-%Y %H:%M") + "\n"
            f.write(fileLine)
            f.flush()
            
            

    # Fin del loop principal
    NetworkWriter.writeToFile(nfq.Q, archivoQ)
    f.close()
    



# -----------------------------
# Uso de la funcion Q aprendida
# -----------------------------
else:

    Experiment.Inicializar(False, True)
         
    # Levanto los pesos de Q del archivo correspondiente
    Q = NetworkReader.readFrom(archivoQ)
    lastTime = time.time()

    while(True):

        # Para salir: ESC
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            elif event.key == K_ESCAPE: pygame.quit()

        
        # Chequeo que haya pasado el tiempo necesario para
        # tomar el siguiente muestreo
        newTime = time.time()
    
        if (newTime - lastTime > tiempoDeMuestreo):

            # Leo el estado actual y ejecuto la accion que minimiza el costo
            estado = Experiment.GetEstado()
            accion = ActionFunctions.GetSiguienteAccionGreedy(estado, Q)

            Experiment.EjecutarAccion(accion)

            # Reinicio contador de tiempo
            lastTime = newTime

            




        
        
        
        
