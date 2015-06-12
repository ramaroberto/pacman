#!/usr/bin/env python

# http://pyode.sourceforge.net/tutorials/tutorial2.html

# pyODE example 2: Connecting bodies with joints

# modified by Gideon Klompje (removed literals and using
# 'ode.Mass.setSphereTotal' instead of 'ode.Mass.setSphere')


import ode
import pygame
import math


from pygame.locals import QUIT, KEYDOWN

class ODESim:
    def __init__(self):
        # Constants
        self.WINDOW_RESOLUTION = (640, 480)

        self.DRAW_SCALE = self.WINDOW_RESOLUTION[0] / 5
        """Factor to multiply physical coordinates by to obtain screen size in pixels"""

        self.DRAW_OFFSET = (self.WINDOW_RESOLUTION[0] / 2, 150)
        """Screen coordinates (in pixels) that map to the physical origin (0, 0, 0)"""

        self.BACKGROUND_COLOR = (255, 255, 255)

        self.GRAVITY = (0, -9.81, 0)

        self.SPHERE1_POSITION = (0, 0, 0)
        self.SPHERE1_MASS = 1
        self.SPHERE1_RADIUS = 0.15
        self.SPHERE1_COLOR = (55, 0, 200)

        self.SPHERE2_POSITION = (0.05, 1, 0)
        self.SPHERE2_MASS = 1
        self.SPHERE2_RADIUS = 0.15
        self.SPHERE2_COLOR = (200, 0, 200)

        self.JOINT1_ANCHOR = (0, 0, 0)
        self.JOINT1_COLOR = (200, 0, 55)
        self.JOINT1_WIDTH = 2
        """Width of the line (in pixels) representing the joint"""

        self.JOINT2_ANCHOR = self.SPHERE1_POSITION
        self.JOINT2_COLOR = (200, 0, 55)
        self.JOINT2_WIDTH = 2
        """Width of the line (in pixels) representing the joint"""

        self.TIME_STEP = 0.01
        self.EPS = 10**-5


        self.original_speed = 0.0
        self.target_speed = 0.0
        self.current_speed = 0.0
        self.pos = 0.0
        self.frame = 0
        # Initialize pygame
        pygame.init()

        # Open a display
        self.screen = pygame.display.set_mode(self.WINDOW_RESOLUTION)

        # Create a world object
        self.world = ode.World()
        self.world.setGravity(self.GRAVITY)
        self.world.setAngularDamping(0.1)


        # Create two bodies
        self.kbody = ode.Body(self.world)
        M = ode.Mass()
        M.setSphereTotal(self.SPHERE1_MASS, self.SPHERE1_RADIUS)
        #kbody.setMass(M)
        self.kbody.setKinematic()
        self.kbody.setPosition(self.SPHERE1_POSITION)

        self.body2 = ode.Body(self.world)
        M = ode.Mass()
        M.setSphereTotal(self.SPHERE2_MASS, self.SPHERE2_RADIUS)
        self.body2.setMass(M)
        self.body2.setPosition(self.SPHERE2_POSITION)
        self.body2.setMaxAngularSpeed(20.0)



        # Connect body2 with kbody
        self.j2 = ode.HingeJoint(self.world)
        self.j2.attach(self.kbody, self.body2)
        self.j2.setAnchor(self.JOINT2_ANCHOR)
        self.j2.setAxis((0,0,1))



        self.clk = pygame.time.Clock()
        self.fps = 1.0 / self.TIME_STEP
        self.cartPole_x = 0.5

        self.xMin = -2.0
        self.xMax = 2.0

        self.acumuladorVueltasPorMovimiento = 1
        self.vueltasPorMovimiento = 10
        self.pos = 0
        self.cartPole_velocidadAngular = 0.0
        self.cartPole_angulo = 0.0


    def run(self, accion):
        movement_scale = 0.02
        if(self.acumuladorVueltasPorMovimiento == self.vueltasPorMovimiento):
            self.acumuladorVueltasPorMovimiento = 0
            self.movimientoSeleccionado = accion
            self.changeSpeed(accion*movement_scale)

        self.acumuladorVueltasPorMovimiento+=1
        self.simLoop()
        self.drawScreen()

            # Try to keep the specified framerate
        self.clk.tick(self.fps)
        return


    # Utility functions
    def coord(self, x, y, integer=False):
        """
        Convert world coordinates to pixel coordinates.  Setting 'integer' to
        True will return integer coordinates.
        """
        xs = (self.DRAW_OFFSET[0] + self.DRAW_SCALE*x)
        ys = (self.DRAW_OFFSET[1] - self.DRAW_SCALE*y)

        if integer:
            return int(round(xs)), int(round(ys))
        else:
            return xs, ys



    def changeSpeed(self, new_speed):

        self.original_speed = self.current_speed
        self.target_speed = new_speed
        self.frame = 0



    def drawScreen(self):
        # Clear the screen
        self.screen.fill(self.BACKGROUND_COLOR)
        # Draw the two bodies and the lines representing the joints
        x1, y1, z1 = self.kbody.getPosition()
        x2, y2, z2 = self.body2.getPosition()
        xj2, yj2, zj2 = self.j2.getAnchor()

        sph1_rad = int(self.DRAW_SCALE * self.SPHERE1_RADIUS)
        sph2_rad = int(self.DRAW_SCALE * self.SPHERE2_RADIUS)

        pygame.draw.line(self.screen, self.JOINT2_COLOR, self.coord(xj2, yj2), self.coord(x2, y2), self.JOINT2_WIDTH)
        pygame.draw.circle(self.screen, self.SPHERE1_COLOR, self.coord(x1, y1, integer=True), sph1_rad, 0)
        pygame.draw.circle(self.screen, self.SPHERE2_COLOR, self.coord(x2, y2, integer=True), sph2_rad, 0)

        font = pygame.font.SysFont("Courier New",18)
        fonttext = font.render("Vel Angular: {0:.1f}   Angulo: {1:.1f}   Posicion: {2:.1f}".format(self.cartPole_velocidadAngular, self.cartPole_angulo, self.cartPole_x) \
                    , 1, (0,0,0), (255,255,255))

        self.screen.blit(fonttext, (50,450))
        pygame.display.flip()
        return


    def scale(self,tup,coef):
        l=[]
        for i in tup:
            l.append(i*coef)
        return tuple(l)

    def substract(self, tup1, tup2):
        assert (len(tup1)==len(tup2))
        l=[]
        for i in xrange(len(tup1)):
            l.append(tup1[i]-tup2[i])
        return tuple(l)

    def simLoop(self):

        if(abs(self.current_speed-self.target_speed)>self.EPS):
            if(self.frame>=self.vueltasPorMovimiento):
                self.current_speed=self.target_speed
            else:
                self.frame+=1
                c = 1.0-0.45**float(self.frame)
                self.current_speed = (self.target_speed*float(c)) + (self.original_speed*(1.0-c))

        vel=(0.0,0.0,0.0)
        self.pos=self.pos-self.current_speed
        next_pos=(self.pos,0.0,0.0)

        curr_pos=self.kbody.getPosition()[0]

        if(curr_pos<self.xMin):
            self.pos = curr_pos = self.xMin
            next_pos=(curr_pos,0.0,0.0)
        elif(curr_pos>self.xMax):
            self.pos = curr_pos = self.xMax
            next_pos=(curr_pos,0.0,0.0)


        vel =  self.scale(self.substract(next_pos,self.kbody.getPosition()), 1.0/self.TIME_STEP)

        self.kbody.setLinearVel(vel)

        self.cartPole_angulo = self.j2.getAngle()
        self.cartPole_velocidadAngular=self.body2.getAngularVel()[2]

        self.cartPole_x=curr_pos

        # Next simulation step
        self.world.step(self.TIME_STEP)

    def Finalizar(self):
        pygame.quit()



