import pygame
import numpy as np
import math
from BazierConroller import BazierController
from theme_AD import *


class Theta_Profile():
    def __init__(self, window=None, font=None):
        self.shot_time = 0
        self.points = None
        self.data_a = None
        self.y = None
        self.x = None
        self.data_dis = None
        self.data_pc = None
        self.current_theta = None
        self.current_percent = None
        self.current_y = None
        self.current_x = None
        self.current_t = None
        self.current_seg = None
        self.B_c_dx = None

        self.window = window
        self.start_point = [0,0]
        self.end_point = [100,0]
        self.draw_scale = [self.window.width/100, self.window.height/(-math.pi*2)]
        self.draw_orgin = [0, self.window.height/2]
        self.Curve = BazierController(self.window,self.start_point,self.end_point, True, False, self.draw_scale, self.draw_orgin)
        self.myfont = font
        self.start_v = 0
        self.end_v = 0
        self.Curve.add_curve()
        self.Curve.update_profile()

        self.b_g = pygame.Surface([self.window.space.width, self.window.height])
        self.b_g.fill(GRAY_2)
        self.offset_x = 0
        self.offset_y = 0

        dev_num_p = 10
        for i in range(0, dev_num_p + 1):
            pygame.draw.line(self.b_g, UI_S, (i * (self.window.width / dev_num_p), 0), (i * (self.window.width / dev_num_p), self.window.height), 1)
            pygame.draw.line(self.b_g, UI_S, (0, i * (self.window.height / dev_num_p)), (self.window.width, i * (self.window.height / dev_num_p)), 1)

    def draw(self, screen):
        self.b_g.fill(GRAY_2)

        dev_num_p = 10
        mod = (self.window.height / dev_num_p)
        self.offset_x = np.mod(self.offset_x, mod)
        self.offset_y = np.mod(self.offset_y, mod)

        for i in range(0, dev_num_p + 1):
            pygame.draw.line(self.b_g, UI_S, (self.offset_x + i * (self.window.width / dev_num_p), 0),
                             (self.offset_x + i * (self.window.width / dev_num_p), self.window.height), 1)
            pygame.draw.line(self.b_g, UI_S, (0, self.offset_y + i * (self.window.height / dev_num_p)),
                             (self.window.width, self.offset_y + i * (self.window.height / dev_num_p)), 1)

        self.Curve.draw(self.b_g)
        #
        # if self.current_x is not None:
        #     l_start = (self.current_x, self.window.top)
        #     l_end = (self.current_x, self.window.bottom)
        #     pygame.draw.line(screen, UI_ES, l_start, l_end, 1)
        #     pygame.draw.circle(screen, UI_ES, (
        #     int(self.current_x), int(self.current_y)), 5)

    def blit(self, screen):
        screen.blit(self.b_g, [self.window.left, self.window.top])

    def add_curve_at_cur(self):
        p = (int(self.current_x), int(self.current_y))
        self.Curve.insert_curve_at(p, self.current_seg, self.current_t)
        self.update_profile()

    def click(self, mouse):
        mouse_rel = np.subtract(mouse, [self.window.left, self.window.top])
        self.Curve.click(mouse_rel)

    def adjust(self, mouse):
        mouse_rel = np.subtract(mouse, [self.window.left, self.window.top])
        self.Curve.adjust(mouse_rel, relative=True)
        self.update_profile()


    def release(self):
        self.Curve.release()

    def handle_event(self, event, mouse_pos, keys):
        if event.button == 4:
            if self.window.space.collidepoint(mouse_pos):
                # if keys[120] == 1:
                #     self.draw_orgin[0] = self.draw_orgin[0] - 2
                #     self.offset_x -= 2
                if keys[121] == 1:
                    self.draw_orgin[1] = self.draw_orgin[1] - 2
                    self.offset_y -= 2

        elif event.button == 5:
            if self.window.space.collidepoint(mouse_pos):
                # if keys[120] == 1:
                #     self.draw_orgin[0] = self.draw_orgin[0] + 2
                #     self.offset_x += 2
                if keys[121] == 1:
                    self.draw_orgin[1] = self.draw_orgin[1] + 2
                    self.offset_y += 2

    def update_profile(self):
        self.Curve.update_profile()
        x, y = zip(*self.Curve.B)
        self.y = np.asarray(y)
        self.x = np.asarray(x)
        self.data_a = self.y
        self.data_pc = self.x

    def get_a_for_t(self, index, t):
        self.current_y = self.Curve.segs[index].y_pos(t)
        self.current_x = self.Curve.segs[index].x_pos(t)
        self.current_theta = self.current_y
        self.current_pc = self.current_x
        self.current_seg = index
        self.current_t = t
        return self.current_theta


    def gen_profile(self):
        self.update_profile()

    def interp_data_per_perc(self, c_p):
        """
        self.data_t ascending 1-D array of time points
        self.data_dis 1-D array of distance at respective time point

        :param c_t: point to be interpolated with in self.data t
        :return:    interpolated distance value for requested time point
        """
        #  ass_check = np.all(np.diff(self.data_t) >= 0)
        #  diff = np.diff(self.data_t)
        #  print(self.data_t)
        #  print(diff)
        self.current_percent = c_p
        self.current_theta = np.interp(c_p,self.data_pc, self.data_a)
        self.current_y = np.interp(c_p,self.data_pc, self.y)
        self.current_x = np.interp(c_p,self.data_pc, self.x)
        self.current_t = np.interp(c_p, self.data_pc, self.Curve.t)
        self.current_seg = np.interp(c_p, self.data_pc, self.Curve.seg_k)
        #  print(c_t, dis, ass_check)
        return self.current_theta