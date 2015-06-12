import pygame, math, sys, time, random
from pygame import draw
from pygame.locals import *

class Simulator:
    
    def __init__(self, imprimirAngulo, imprimirTiempo):

        self.imprimirAngulo = imprimirAngulo        # Imprime angulo y velocidad angular en pantalla
        self.imprimirTiempo = imprimirTiempo        # Imprime cantidad de tiempo que mantiene seguido en la region target
        self.targetValue = 0.5
        

        # Inicializo variables
        self.GRAVITY = 9.8
        self.MASSCART = 10.0
        self.MASSPOLE = 0.3
        self.TOTAL_MASS = (self.MASSPOLE + self.MASSCART)
        self.LENGTH = 0.5 # actually half the pole's length
        self.POLEMASS_LENGTH = (self.MASSPOLE * self.LENGTH)
        self.FORCE_MAG = 10.0
        self.TAU = 0.02 # dt
        self.FOURTHIRDS = 1.3333333333333
        
        self.vueltas = 0
        self.movimientoSeleccionado = 0
        self.vueltasPorMovimiento = 5  #cada cuantas vueltas del TAU va a durar una desicion
        self.acumuladorVueltasPorMovimiento = self.vueltasPorMovimiento
        self.movTotales = 1
        self.movimientoTemporario = 0
        self.aplicacionFuerza = 0
        
        self.screenWidth = 1000
        self.cartWidth = 80
        self.altura = 150

        self.cartPole_x = 0.5
        self.cartPole_velocidadX = 0.0
        self.cartPole_angulo = math.pi
        self.cartPole_velocidadAngular = 0.0

        self.enObjetivo = False         # Indica si el pendulo esta dentro del angulo objetivo - para contador de tiempo
        self.enObjetivo_tiempoDeInicio = 0
        self.enObjetivo_tiempoMaximo = 0
        self.enObjetivo_ultimoTiempo = 0

        #self.colorCarro = (255,0,0)
        #self.colorPelota = (100,100,100)
        self.colorCarro = (150, 0, 0)
        self.colorPendulo = (0, 100, 0)
        self.colorPelota = (92, 51, 23)

        
        self.xMin = 0
        self.xMax = 1

        
        self.fastMotion = False


        # Inicializo pygame
        pygame.init()
        pygame.display.set_caption('Cart Pole Balancing')


        #Inicializo pantalla

        self.background = pygame.image.load("imgs/bg2.jpg")
        #self.texturaCarro = pygame.image.load("imgs/carro2.jpg")
        self.backgroundRect = self.background.get_rect()

        self.x_size, self.y_size = 1000, 480
        self.screen = pygame.display.set_mode((self.x_size, self.y_size))
        self.clock = pygame.time.Clock()
        self.position = self.x_size/2, self.y_size - 100
        self.height = -100
        self.top_position = self.position[0], self.position[1] + self.height
        self.clock.tick(1/self.TAU)

        
    
    def calcPhysics(self):
        
        force = (self.movimientoSeleccionado*250) * (1 + random.random()/10 - 0.05)

        if self.movimientoSeleccionado != 0:
            self.movimientoSeleccionado = 0
            self.aplicacionFuerza = self.vueltasPorMovimiento
            self.cartPole_velocidadX = 0

        self.aplicacionFuerza = self.aplicacionFuerza-1
        
        #print "FORCE {}, vueltas: {}".format(self.force, self.vueltas)

        costheta = math.cos(self.cartPole_angulo)
        sintheta = math.sin(self.cartPole_angulo)

        temp = ((force + self.POLEMASS_LENGTH * self.cartPole_velocidadAngular * \
                 self.cartPole_velocidadAngular * sintheta)
                             / self.TOTAL_MASS)

        gravedadModificada = self.GRAVITY

        # Intento de rozamiento
        if self.cartPole_angulo > 0:
            if self.cartPole_velocidadAngular > 0:
                gravedadModificada = gravedadModificada * 0.8
            else:
                gravedadModificada = gravedadModificada * 1.2
        else:
            if self.cartPole_velocidadAngular > 0:
                gravedadModificada = gravedadModificada * 1.2
            else:
                gravedadModificada = gravedadModificada * 0.8

            
        thetaacc = ((gravedadModificada * sintheta - costheta* temp)
                   / (self.LENGTH * (self.FOURTHIRDS - self.MASSPOLE * costheta * costheta
                                                  / self.TOTAL_MASS)))

        xacc  = temp - self.POLEMASS_LENGTH * thetaacc* costheta / self.TOTAL_MASS

        # Update the four state variables, using Euler's method.

        self.cartPole_x  += self.TAU * self.cartPole_velocidadX
        self.cartPole_velocidadX += self.TAU * xacc
        
        if (self.aplicacionFuerza <= 0):
            self.aplicacionFuerza = 0
            self.cartPole_velocidadX = 0
            
        self.cartPole_angulo += self.TAU * self.cartPole_velocidadAngular
        self.cartPole_velocidadAngular += self.TAU * thetaacc

        while self.cartPole_angulo > math.pi:
            self.cartPole_angulo -= 2.0 * math.pi

        while self.cartPole_angulo < -math.pi:
            self.cartPole_angulo += 2.0 * math.pi



    def run(self, accion):

        if(self.acumuladorVueltasPorMovimiento == self.vueltasPorMovimiento):
            self.acumuladorVueltasPorMovimiento = 0

            self.movimientoSeleccionado = accion

            # Bordes
            if self.cartPole_x >= 1 and self.movimientoSeleccionado == 1:
                self.cartPole_x = 1
                self.movimientoSeleccionado = 0

            if self.cartPole_x <= 0 and self.movimientoSeleccionado == -1:
                self.cartPole_x = 0
                self.movimientoSeleccionado = 0
            
        self.acumuladorVueltasPorMovimiento = self.acumuladorVueltasPorMovimiento + 1


        # RENDERING
        self.calcPhysics()

        tetha = self.cartPole_angulo
        length = 150
        
        self.position = self.cartPole_x*(self.screenWidth/self.movTotales), self.y_size - self.altura - 25
        self.top_position = int(self.position[0] + math.sin(tetha)*length), \
                    int(self.position[1] - math.cos(tetha)*length)

        self.fastMotion = False
        
        if self.fastMotion:
            self.clock.tick(200)
            self.screen.fill((200,200,255))
        else:
            self.screen.fill((255,255,255))                    
            self.clock.tick(1/self.TAU)


        self.screen.blit(self.background, self.backgroundRect)
        
        base = pygame.Rect(0,0,75,50)
        base.center = self.position

        floor = pygame.Rect(0, 0, self.x_size, self.altura)
        floor.bottom = self.y_size
        draw.rect(self.screen, (20,20,20), floor)
        

        # Carro
        draw.rect(self.screen, self.colorCarro , base)
        #self.screen.blit(self.texturaCarro, base, pygame.Rect(0,0,75,50))
        draw.line(self.screen, self.colorPendulo, self.position, self.top_position, 4)
        draw.circle(self.screen, self.colorPelota, self.top_position, 10)

        # Texto
        font = pygame.font.SysFont("Arial", 18, bold = True)
        textAngulo = font.render("Vel Angular: {0:.1f}   Angulo: {1:.1f} ".format(self.cartPole_velocidadAngular, self.cartPole_angulo) \
                    , 1, (0,0,0))

        if self.imprimirAngulo:
            self.screen.blit(textAngulo, (50, 30))

        if self.imprimirTiempo:

            # Chequeo si llego a la zona objetivo,
            # y si es la primera vez que entra
            if abs(self.cartPole_angulo) <= self.targetValue:

                if not self.enObjetivo:
                    # Primera vez que llega
                    self.enObjetivo = True;
                    self.enObjetivo_tiempoDeInicio = time.time()
                    tiempoTranscurrido = 0

                else:
                    tiempoTranscurrido = time.time() - self.enObjetivo_tiempoDeInicio
    
                self.enObjetivo_ultimoTiempo = tiempoTranscurrido
                
            else:    
                self.enObjetivo = False
                tiempoTranscurrido = 0


            if (tiempoTranscurrido > self.enObjetivo_tiempoMaximo):
                self.enObjetivo_tiempoMaximo = tiempoTranscurrido
                
            textTiempo = font.render("Tiempo Arriba: {0:.2f}".format(self.enObjetivo_ultimoTiempo), 1, (0, 0, 0))
            textTiempoMaximo = font.render("Maximo: {0:.2f} segundos".format(self.enObjetivo_tiempoMaximo), 1, (0, 0, 0))

            self.screen.blit(textTiempo, (750, 30))
            #self.screen.blit(textUltimoTiempo, (750, 50))
            self.screen.blit(textTiempoMaximo, (750, 50))

        pygame.display.flip()


    def Finalizar(self):
        pygame.quit()


    def GetKeyPressed(self):
        return pygame.key.get_pressed()
        
        
