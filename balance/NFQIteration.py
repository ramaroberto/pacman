from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers.rprop import RPropMinusTrainer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import FeedForwardNetwork, SigmoidLayer, FullConnection

from RLObjects import Posicion, Accion, Estado

class NFQIteration:

    _gamma = 0.9
    _epochs = 500      #1000
    _epochsNN = 100
    
    def __init__(self):

        self.Q = FeedForwardNetwork()


        # La funcion de valor se representa con una red neuronal
        # Input: S = (Angulo, Velocidad angular, Posicion), A = accion
        # Output: Valor
        # 2 capas ocultas de 5 neuronas cada una
        # Funcion de activacion sigmoidea
        inLayer = SigmoidLayer(4, name="Input Layer")
        hiddenLayer1 = SigmoidLayer(5, name="Hidden Layer 1")
        hiddenLayer2 = SigmoidLayer(5, name="Hidden Layer 2")
        outLayer = SigmoidLayer(1, name="Output Layer")

        self.Q.addInputModule(inLayer)
        self.Q.addModule(hiddenLayer1)
        self.Q.addModule(hiddenLayer2)
        self.Q.addOutputModule(outLayer)

        connInToHidden1 = FullConnection(inLayer, hiddenLayer1)
        connHidden1ToHidden2 = FullConnection(hiddenLayer1, hiddenLayer2)
        connHidden2ToOut = FullConnection(hiddenLayer2, outLayer)

        self.Q.addConnection(connInToHidden1)
        self.Q.addConnection(connHidden1ToHidden2)
        self.Q.addConnection(connHidden2ToOut)

        self.Q.sortModules()



    def train(self, transitionSamples):

        print "Entrenando..."
         
        k = 0
        trainer = RPropMinusTrainer(self.Q, batchlearning=True)
        #trainer = BackpropTrainer(self.Q, batchlearning=False)
        TS = SupervisedDataSet(4, 1)
        
        while (k < self._epochs):

            if k % 10 == 0:
                print "\t ", k
                
            # Genero training set en base a las muestras
            # Input: Vector de 4 dimensiones (angulo, vel.angular, pos, accion)
            # Target: Valor
            
            TS.clear()
            
            for s, a, s_1, costo in transitionSamples:

                # Tomo Q para s', para todas las acciones posibles
                # (vector con el valor para s', para cada una de las 3 acciones posibles)
                # Q_s1 = [ self.Q.activate([s_1.angulo, s_1.velocidadAngular, s_1.posicion, b]) for b in range(Accion.maxValor + 1) ]
                valDerecha = self.Q.activate([s_1.angulo, s_1.velocidadAngular, s_1.posicion, Accion.DERECHA])
                valIzquierda = self.Q.activate([s_1.angulo, s_1.velocidadAngular, s_1.posicion, Accion.IZQUIERDA])
                
                
                if valDerecha >= 1 or valDerecha <= 0:
                        print "Q incorrecta: ", valDerecha

                if valIzquierda >= 1 or valIzquierda <= 0:
                        print "Q incorrecta: ", valIzquierda
                        
                # Input y Target para la red neuronal
                inputVal = (s.angulo, s.velocidadAngular, s.posicion, a)
                
                if costo == 0:
                    targetVal = costo
                else:
                    targetVal = costo + self._gamma * min(valDerecha, valIzquierda)

                if targetVal > 1 or targetVal < 0:
                    print "Target incorrecto: ", targetVal


                TS.addSample(inputVal, targetVal)

            # Entreno la red neuronal
            trainer.setData(TS)
            trainer.train()     # 1 epoch
            #trainer.trainEpochs(self._epochsNN)
                

            k = k + 1
        
