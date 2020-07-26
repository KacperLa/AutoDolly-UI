import pygame
import numpy as np
from BazierConroller import BazierController
from theme_AD import *


class Velocity_Manual():
    def __init__(self, window, font):
        self.window = window
        self.start_point = [self.window.left,self.window.bottom]
        self.end_point = [self.window.right,self.window.top]

        self.Curve = BazierController(self.window,self.start_point,self.end_point, True, True)
        self.myfont = font
        self.y_max = self.window.top
        self.start_v = 0
        self.end_v = 1
        self.Curve.add_curve()
        self.Curve.update_profile()
        self.points = None
        self.B_c_dx = None
        self.Z = None
        self.rev = False
        self.v = None

    def draw(self, screen):
        self.Curve.draw(screen)
        if self.Z is not None:
            l_start = (self.window.p_calc(self.Z, "x"), self.window.top)
            l_end = (self.window.p_calc(self.Z, "x"), self.window.bottom)
            pygame.draw.line(screen, UI_ES, l_start, l_end, 1)
            pygame.draw.circle(screen, UI_ES, (int(self.window.p_calc(self.Z, "x")),int(self.window.p_calc(self.v, "y"))), 5)

    def click(self, mouse):
        self.Curve.click(mouse)

    def adjust(self, mouse):
        self.Curve.adjust(mouse)

    def release(self):
        self.Curve.release()

    def update_profile(self):
        self.Curve.update_profile()

    def scale_v(self):
        if not self.Z == 0:
            if self.Z < 0:
                self.rev = True
                Z_n = self.Z * -1
            else:
                self.rev = False
                Z_n = self.Z * 1

            #print(self.Z, Z_n)

            if self.Curve.segs is not None:
                self.Curve.update_profile()
                y_scale = (self.window.bottom - self.window.top)/1
                t = self.Curve.segs[0].get_t_for_x(Z_n*100)
                #print(t,self.window.left,self.window.right)
                if not t == None:
                    y = self.Curve.segs[0].y_pos(t)
                    print(y, self.window.top, self.window.bottom)
                    v_n = (-1 * (y - self.Curve.start_point[1])) / y_scale
                else:
                    v_n = 0
            if self.rev == True:
                self.v = v_n * -1.0
            else:
                self.v = v_n

        else:
            self.v = 0
        return self.v