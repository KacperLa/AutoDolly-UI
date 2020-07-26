from BazierConroller import BazierController
import numpy as np
import pygame
from theme_AD import *

class Position_Controller():
    def __init__(self, window=None, s_pt=None, e_pt=None):
        self.current_x = 0
        self.current_y = 0
        self.current_p_c = 0
        self.current_t = 0
        self.current_seg = 0

        self.window = window
        self.draw_scale = [self.window.width/10, self.window.height/-10]
        self.draw_orgin = [self.window.width/2, self.window.height/2]

        self.start_point = [0, 0]
        self.end_point =  [3,3]

        self.Curve = BazierController(window,self.start_point,self.end_point, False, False, self.draw_scale, self.draw_orgin)
        self.Curve.add_curve()
        self.Curve.update_profile()
        self.Curve.segs[0].p0.lock = True
        self.current_x = self.start_point[0]
        self.current_y = self.start_point[1]
        _current_pos = [self.current_x, self.current_y]
        self.draw_current_pos = np.add(np.multiply(_current_pos, self.draw_scale), self.draw_orgin)

        self.b_g = pygame.Surface([self.window.space.width, self.window.height])
        self.b_g.fill(GRAY_2)
        self.offset_x = 0
        self.offset_y = 0

        dev_num_p = 10
        for i in range(0, dev_num_p + 1):
            pygame.draw.line(self.b_g, UI_S, (i * (self.window.width / dev_num_p), 0), (i * (self.window.width / dev_num_p), self.window.height), 1)
            pygame.draw.line(self.b_g, UI_S, (0, i * (self.window.height / dev_num_p)), (self.window.width, i * (self.window.height / dev_num_p)), 1)

    def gen_profile(self, t):
        self.Curve.update_profile()
        y_scale = (self.Curve.start_point[1] - self.Curve.window.tom)
        x_scale = t / (self.Curve.end_point[0] - self.Curve.start_point[0])
        with open('Velocity Profile.txt', 'w') as vpf:
            for num_thing, current in enumerate(self.Curve.segs):
                for xy, a in zip(current.B, current.B_t):
                    x, y= xy
                    a = a
                    y = (-1 * (y - self.Curve.start_point[1])) / y_scale
                    x = (x - self.Curve.start_point[0]) * x_scale
                    # print(x, y)
                    vpf.write(str(x) + ", " + str(y) + ", " + str(a) + "\n")

    def find_xya_per_dis(self,dis):
        dis = dis
        full_length = 0
        index_saved = 0
        pre_length = 0
        for index, current in enumerate(self.Curve.segs):
            full_length = full_length + current.length
            if full_length <= dis:
                index_saved = index+1
                pre_length = pre_length + current.length

        if index_saved > len(self.Curve.segs)-1:
            print("Length of path exceeded")
            index_saved = len(self.Curve.segs)-1
            t = 1
        else:
            local_dis = dis - pre_length
            t = self.Curve.segs[index_saved].get_t_for_length(local_dis)
        self.current_x = self.Curve.segs[index_saved].x_pos(t)
        self.current_y = self.Curve.segs[index_saved].y_pos(t)
        self.current_p_c = dis/self.Curve.length
        self.current_seg = index_saved
        self.current_t = t
        a = self.Curve.segs[index_saved].slope(t)
        _current_pos = [self.current_x, self.current_y]
        self.draw_current_pos = np.add(np.multiply(_current_pos, self.draw_scale), self.draw_orgin)
        return self.current_x, self.current_y, a

    def add_curve_at_cur(self):
        p = (self.current_x, self.current_y)
        self.Curve.insert_curve_at(p, self.current_seg, self.current_t)
        self.update_profile()

    def draw(self):
        self.b_g.fill(GRAY_2)

        dev_num_p = 10
        mod = (self.window.width / dev_num_p)
        self.offset_x = np.mod(self.offset_x, mod)
        self.offset_y = np.mod(self.offset_y, mod)

        for i in range(0, dev_num_p + 1):
            pygame.draw.line(self.b_g, UI_S, (self.offset_x + i * (self.window.width / dev_num_p), 0),
                             (self.offset_x + i * (self.window.width / dev_num_p), self.window.height), 1)
            pygame.draw.line(self.b_g, UI_S, (0, self.offset_y + i * (self.window.height / dev_num_p)),
                             (self.window.width, self.offset_y + i * (self.window.height / dev_num_p)), 1)

        self.Curve.draw(self.b_g)

    def blit(self, screen):
        screen.blit(self.b_g, [self.window.left, self.window.top])

    def click(self, mouse):
        mouse_rel = np.subtract(mouse, [self.window.left, self.window.top])
        self.Curve.click(mouse_rel)

    def release(self):
        self.Curve.release()

    def adjust(self, mouse):
        mouse_rel = np.subtract(mouse, [self.window.left, self.window.top])
        self.Curve.adjust(mouse_rel, relative=True)

    def update_profile(self):
        self.Curve.update_profile()

    def handle_event(self, event, mouse_pos, keys):
        if event.button == 4:
            if self.window.space.collidepoint(mouse_pos):
                if keys[120] == 1:
                    self.draw_orgin[0] = self.draw_orgin[0] - 2
                    self.offset_x -= 2
                if keys[121] == 1:
                    self.draw_orgin[1] = self.draw_orgin[1] - 2
                    self.offset_y -= 2

        elif event.button == 5:
            if self.window.space.collidepoint(mouse_pos):
                if keys[120] == 1:
                    self.draw_orgin[0] = self.draw_orgin[0] + 2
                    self.offset_x += 2
                if keys[121] == 1:
                    self.draw_orgin[1] = self.draw_orgin[1] + 2
                    self.offset_y += 2