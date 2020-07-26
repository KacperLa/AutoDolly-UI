import numpy as np
import math
import pygame
import  os
from theme_AD import *
from UI_Elements import ctrl_point
import json


class segment:
    def __init__(self, res, P0, P3, UI_orgin, UI_scale, draw=True):
        self.res = 100
        self.B = None
        self.B_x = None
        self.B_y = None
        self.B_c_dx = None
        self.B_t = None
        self.t_a = None
        self.length = 0
        self.Draw = draw

        if not draw:
            self.p0 = ctrl_point([0,0])
            self.p1 = ctrl_point([0,0])
            self.p2 = ctrl_point([0,0])
            self.p3 = ctrl_point([0,0])
        else:
            self.UI_orgin = UI_orgin
            self.UI_scale = UI_scale
            self.mv = [False, False, False, False]
            self.moving = False
            x1 = P0[0]+(P3[0]-P0[0])/3
            y1 = P0[1]+(P3[1]-P0[1])/3
            x2 = P0[0]+((P3[0]-P0[0])/3.0)*2.0
            y2 = P0[1]+((P3[1]-P0[1])/3.0)*2.0
            self.p0 = ctrl_point(P0, self.UI_orgin, self.UI_scale, RED)
            self.p1 = ctrl_point([x1, y1], self.UI_orgin, self.UI_scale, BACKGROUND)
            self.p2 = ctrl_point([x2, y2], self.UI_orgin, self.UI_scale, BACKGROUND)
            self.p3 = ctrl_point(P3, self.UI_orgin, self.UI_scale, RED)
            self.calc_curve()
            self.length = self.length_up_to_t(1.0)

        self.cps = [self.p0, self.p1, self.p2, self.p3]

    def reset(self):
        p0 = self.p0.point
        p3 = self.p3.point
        x1 = p0[0] + (p3[0] - p0[0]) / 3
        y1 = p0[1] + (p3[1] - p0[1]) / 3
        x2 = p0[0] + ((p3[0] - p0[0]) / 3.0) * 2.0
        y2 = p0[1] + ((p3[1] - p0[1]) / 3.0) * 2.0
        self.p1.point = [x1,y1]
        self.p2.point = [x2,y2]

    def update_points(self, P0, P3):
        self.p0.point[0] = P0
        self.p3.point[3] = P3

    def calc_curve(self):
        t = np.linspace(0, 1, self.res, True)
        x = self.x_pos(t)
        y = self.y_pos(t)
        a = self.slope(t)
        b = zip(x, y)
        self.B_x = x
        self.B_y = y
        self.B = list(b)
        self.B_t = a
        self.t_a = t

    def calc_curve_c_dx(self):
        x = []
        y = []
        a = []
        t_a = []
        for x_p in range(1,self.res+1):
            if x_p == 1:
                t = 0
            elif x_p == self.res:
                t = 1
            else:
                t = self.get_t_for_x(x_p)
            t_a.append(t)
            x.append(self.x_pos(t))
            y.append(self.y_pos(t))
            a.append(self.slope(t))
        self.t_a = t_a
        self.B_c_dx = list(zip(x,y))
        self.B_t = a

    def draw(self, screen):
        _B = self.B
        if self.UI_scale is not None:
            _B = np.multiply(_B, self.UI_scale)
        if self.UI_orgin is not None:
            _B = np.add(_B, self.UI_orgin)
        pygame.draw.aalines(screen, RED, False, _B, 0)
        pygame.draw.aaline(screen, BACKGROUND, self.cps[0].draw_point, self.cps[1].draw_point, 2)
        pygame.draw.aaline(screen, BACKGROUND, self.cps[2].draw_point, self.cps[3].draw_point, 2)

        for cp in self.cps:
            cp.update()
            cp.draw(screen)

    def update(self):
        for cp in self.cps:
            cp.update()
            self.length = self.length_up_to_t(1.0)

    def click(self,mouse):
        for index, cp in enumerate(self.cps):
            cp.click(mouse)
            self.mv[index] = cp.moving
        if True in self.mv:
            self.moving = True

    def adjust(self, mouse):
        for cp in self.cps:
            if cp.moving:
                cp.move(mouse)

    def release(self):
        for cp in self.cps:
            cp.release()
        self.mv = [False,False,False,False]
        self.moving = False

    def x_pos(self, t):
        x = self.p0.point[0] * (1.0 - t) ** 3.0 + self.p1.point[0] * 3.0 * t * (1.0 - t) ** 2.0 + self.p2.point[0] * 3.0 * (
                    1.0 - t) * t ** 2.0 + self.p3.point[0] * t ** 3.0
        return x

    def y_pos(self, t):
        y = self.p0.point[1] * (1.0 - t) ** 3.0 + self.p1.point[1] * 3.0 * t * (1.0 - t) ** 2.0 + self.p2.point[1] * 3.0 * (
                    1.0 - t) * t ** 2.0 + self.p3.point[1] * t ** 3.0
        return y

    def dx_pos(self, t):
        dx = 3.0 * (self.p1.point[0] - self.p0.point[0]) * (1.0 - t) ** 2.0 + 6.0 * (1.0 - t) * t * (
                    self.p2.point[0] - self.p1.point[0]) + 3.0 * (self.p3.point[0] - self.p2.point[0]) * t ** 2.0
        return dx

    def dy_pos(self, t):
        dy = 3.0 * (self.p1.point[1] - self.p0.point[1]) * (1.0 - t) ** 2.0 + 6.0 * (1.0 - t) * t * (
                    self.p2.point[1] - self.p1.point[1]) + 3.0 * (self.p3.point[1] - self.p2.point[1]) * t ** 2.0
        return dy

    def slope(self, t):
        a = np.arctan2(self.dy_pos(t), self.dx_pos(t))
        return a

    def mag(self, x1, y1, x2, y2):
        m = math.sqrt((x2 - x1) ** 2.0 + (y2 - y1) ** 2.0)
        return m

    def limit(self, x, min_val, max_val):
        if x < min_val:
            return min_val
        if x > max_val:
            return max_val
        else:
            return x

    def get_t_for_x(self, pos):
        a = self.p0.point[0]
        b = self.p1.point[0]
        c = self.p2.point[0]
        d = self.p3.point[0]
        x = a + (((d - a)/self.res)*pos)
        na = -a + 3.0*b - 3.0*c + d
        nb = 3.0*a - 6.0*b + 3.0*c
        nc = -3.0*a + 3.0*b
        nd = a - x

        coeff = [na, nb, nc, nd]
        roots = np.roots(coeff)
        for each in roots:
            root = self.accept(each)
            if root is not None:
                return abs(np.real(root))

    def accept(self,t):
        if t.imag == 0:
            if 0 <= t.real <= 1:
                return t
            else:
                return None
        else:
            return None

    def length_up_to_t(self, end_point):  # function that calculates the length up to t (0.0 - 1.0)
        end_point = self.limit(end_point, 0.0, 1.0)
        approx_res = int(1000.0 * end_point)
        li = 0
        t = np.linspace(0, end_point, approx_res, True)
        x = self.x_pos(t)
        y = self.y_pos(t)
        b = list(zip(x, y))
        for num, pts in enumerate(b):
            if num > 0:
                    li = li + self.mag(pts[0], pts[1], b[num - 1][0], b[num - 1][1])
        return li

    def get_t_for_length(self, s): # cal
        t = s / self.length
        error = 0.0005
        iterations = 0
        upper = 1.0
        lower = 0.0
        while True:

            length_der = self.mag(0, 0, self.dx_pos(t), self.dy_pos(t))
            length = self.length_up_to_t(t)
            t_next = t - ((length - s) / length_der)
            #  print("iterations", iterations, "t", t, "tnext", t_next, "length_der", length_der, "length", length, "self.length", self.length)

            if math.fabs(t_next - t) < error:
                #  print("done")
                break
            t = t_next
            iterations = iterations + 1
            if iterations > 1000:
                #  print("iteration limit reached")
                break
        return t

class BazierController:
    def __init__(self, window=None, start_point=None, end_point=None, lock_x=None, lock_y=None, scale=None, orgin=None):
        self.res = 100
        self.segs = None
        self.cps = []
        self.res_per_seg = 100
        self.length = None
        self.num_points = 0
        self.B = []
        self.t = []
        self.seg_k = []
        self.shot_time = None
        self.start_point = [0,0]
        self.end_point = [0,0]
        self.UI_orgin = None
        self.UI_scale = None

        if window is not None:
            self.Draw = True
            self.window = window
            if orgin == None:
                self.UI_orgin = [window.left, window.bottom]
            else:
                self.UI_orgin = orgin
            self.UI_scale = scale
            self.start_point = start_point
            self.end_point = end_point
            self.start_end_lock_x = lock_x
            self.start_end_lock_y = lock_y
            self.moving = False
        else:
            self.Draw = False

    def insert_curve_at(self, p, index=None, t=None):
        index = int(index)
        c_seg = self.segs[index]
        if t is not None:
            p0 = self.segs[index].p0.point
            p1 = self.segs[index].p1.point
            p2 = self.segs[index].p2.point
            p3 = self.segs[index].p3.point
        self.segs.insert(index+1,segment(100, p, c_seg.p3.point, self.UI_orgin, self.UI_scale, draw=self.Draw))

        if t is not None:
            n_a_p1 = [p0[0] + ((p1[0] - p0[0]) * (t)), p0[1] + ((p1[1] - p0[1]) * (t))]
            n_b_p2 = [p2[0] + ((p3[0] - p2[0]) * (t)), p2[1] + ((p3[1] - p2[1]) * (t))]
            m_p12 = [p1[0] + ((p2[0] - p1[0]) * (t)), p1[1] + ((p2[1] - p1[1]) * (t))]
            n_a_p2 = [m_p12[0] + ((n_a_p1[0] - m_p12[0]) * (1 - t)), m_p12[1] + ((n_a_p1[1] - m_p12[1]) * (1 - t))]
            n_b_p1 = [m_p12[0] + ((n_b_p2[0] - m_p12[0]) * (t)), m_p12[1] + ((n_b_p2[1] - m_p12[1]) * (t))]
            self.segs[index+1].p1.point = n_b_p1
            self.segs[index+1].p2.point = n_b_p2
            self.segs[index].p1.point = n_a_p1
            self.segs[index].p2.point = n_a_p2
            self.segs[index].p3.point = p
        else:
            self.segs[index].p3.point = p
            self.segs[index].reset()
        self.update_profile()

    def insert_curve(self, index):
        s_l = len(self.segs)+1
        c_seg = self.segs[index]
        m_p = [c_seg.p0.point[0] + (c_seg.p3.point[0]-c_seg.p0.point[0])/2,c_seg.p0.point[1] + (c_seg.p3.point[1]-c_seg.p0.point[1])/2]
        self.segs.insert(index+1,segment(100, m_p, c_seg.p3.point, self.UI_orgin, self.UI_scale, draw=self.Draw))
        self.segs[index].p3.point = m_p
        self.segs[index].reset()
        self.update_profile()

    def add_curve(self):
        if self.segs is None:
            self.segs = []
        index = len(self.segs) + 1
        if index == 1:
            start_point = self.start_point
        else:
            #  self.equal_space()
            start_point = self.segs[index - 2].p3.point
        seg_name = "seg_" + str(index)
        inter_space = (self.end_point[0] - self.start_point[0]) / index
        self.segs.append(segment(inter_space, start_point, self.end_point, self.UI_orgin, self.UI_scale, draw=self.Draw))
        self.update_profile()

    def clear_all(self):
        self.segs = None

    def draw(self, screen, t=None):
        if self.segs is not None:
            for thing in self.segs:
                thing.draw(screen)
                if t is not None:
                    p0 = thing.p0.point
                    p1 = thing.p1.point
                    p2 = thing.p2.point
                    p3 = thing.p3.point
                    n_a_p1 = [p0[0] + ((p1[0] - p0[0]) * (t)), p0[1] + ((p1[1] - p0[1]) * (t))]
                    n_b_p2 = [p2[0] + ((p3[0] - p2[0]) * (t)), p2[1] + ((p3[1] - p2[1]) * (t))]
                    m_p12 = [p1[0] + ((p2[0] - p1[0]) * (t)), p1[1] + ((p2[1] - p1[1]) * (t))]
                    n_a_p2 = [m_p12[0] + ((n_a_p1[0] - m_p12[0]) * (1 - t)), m_p12[1] + ((n_a_p1[1] - m_p12[1]) * (1 - t))]
                    n_b_p1 = [m_p12[0] + ((n_b_p2[0] - m_p12[0]) * (t)), m_p12[1] + ((n_b_p2[1] - m_p12[1]) * (t))]
                    pygame.draw.line(screen, RED, n_a_p1, m_p12, 1)
                    pygame.draw.line(screen, RED, m_p12, n_b_p2 , 1)
                    pygame.draw.line(screen, RED, n_a_p2, n_b_p1, 1)

    def click(self, mouse):
        if self.segs is not None:
            for current in self.segs:
                current.click(mouse)
                if current.moving:
                    self.moving = True

    def adjust(self, mouse, relative=False):
        if self.Draw:
            if not relative:
                l_bound = self.window.left
                t_bound = self.window.top
                r_bound = self.window.right
                b_bound = self.window.bottom
            else:
                l_bound = 0
                t_bound = 0
                r_bound = self.window.width
                b_bound = self.window.height


            if mouse[0] < l_bound:
                mouse = [l_bound, mouse[1]]
            if mouse[0] > r_bound:
                mouse = [r_bound, mouse[1]]
            if mouse[1] > b_bound:
                mouse = [mouse[0], b_bound]
            if mouse[1] < t_bound:
                mouse = [mouse[0], t_bound]

            self.update_profile()


        for index,current in enumerate(self.segs):
            current.adjust(mouse)
            _mouse = np.divide(np.subtract(mouse, self.UI_orgin), self.UI_scale)
            if current.moving:
                if self.start_end_lock_x and not self.start_end_lock_y:
                    if index == 0 and current.mv[0]:
                        current.p0.move_og([self.start_point[0],_mouse[1]])
                    elif index == len(self.segs)-1 and current.mv[3]:
                        current.p3.move_og([self.end_point[0],_mouse[1]])
                elif self.start_end_lock_y and not self.start_end_lock_x:
                    if index == 0 and current.mv[0]:
                        current.p0.move_og([_mouse[0],self.start_point[1]])
                    elif index == len(self.segs)-1 and current.mv[3]:
                        current.p3.move_og([_mouse[0],self.end_point[1]])
                elif self.start_end_lock_y and self.start_end_lock_x:
                    if index == 0 and current.mv[0]:
                        current.p0.move_og(self.start_point)
                    elif index == len(self.segs)-1 and current.mv[3]:
                        current.p3.move_og(self.end_point)
                else:
                    if index == 0 and current.mv[0]:
                        next_y = current.p1.draw_point[1] - current.p0.draw_point_prev[1]
                        next_x = current.p1.draw_point[0] - current.p0.draw_point_prev[0]
                        current.p1.move([mouse[0] + next_x, mouse[1] + next_y])

                    if index == len(self.segs) - 1 and current.mv[3]:
                        prev_y = current.p2.draw_point[1] - current.p3.draw_point_prev[1]
                        prev_x = current.p2.draw_point[0] - current.p3.draw_point_prev[0]
                        current.p2.move([mouse[0] + prev_x, mouse[1] + prev_y])

                if current.mv[0] and not index == 0:
                    prev_seg = self.segs[index - 1]
                    prev_y = prev_seg.p2.draw_point[1] - current.p0.draw_point_prev[1]
                    prev_x = prev_seg.p2.draw_point[0] - current.p0.draw_point_prev[0]
                    next_y = current.p1.draw_point[1] - current.p0.draw_point_prev[1]
                    next_x = current.p1.draw_point[0] - current.p0.draw_point_prev[0]
                    prev_seg.p2.move([mouse[0] + prev_x, mouse[1] + prev_y])
                    current.p1.move([mouse[0] + next_x, mouse[1] + next_y])

                if current.mv[1] and not index == 0:
                    x = current.p0.draw_point[0] - current.p1.draw_point[0]
                    y = current.p0.draw_point[1] - current.p1.draw_point[1]
                    angle = -math.atan2(x, y)
                    prev = self.segs[index - 1]
                    x_prev = prev.p3.draw_point[0] - prev.p2.draw_point[0]
                    y_prev = prev.p3.draw_point[1] - prev.p2.draw_point[1]
                    mag = math.sqrt((x_prev ** 2) + (y_prev ** 2))
                    new_x = prev.p3.draw_point[0] + mag * math.cos(angle - math.pi - math.pi / 2)
                    new_y = prev.p3.draw_point[1] + mag * math.sin(angle - math.pi - math.pi / 2)
                    prev.p2.move([new_x, new_y])

                if current.mv[2] and not index == len(self.segs) - 1:
                    x = current.p3.draw_point[0] - current.p2.draw_point[0]
                    y = current.p3.draw_point[1] - current.p2.draw_point[1]
                    angle = -math.atan2(x, y)
                    next_seg = self.segs[index + 1]
                    x_next = next_seg.p0.draw_point[0] - next_seg.p1.draw_point[0]
                    y_next = next_seg.p0.draw_point[1] - next_seg.p1.draw_point[1]
                    mag = math.sqrt((x_next ** 2) + (y_next ** 2))
                    new_x = next_seg.p0.draw_point[0] + mag * math.cos(angle - math.pi - math.pi / 2)
                    new_y = next_seg.p0.draw_point[1] + mag * math.sin(angle - math.pi - math.pi / 2)
                    next_seg.p1.move([new_x, new_y])

    def release(self):
        self.moving = False
        if self.segs is not None:
            for seg in self.segs:
                seg.release()

    def update_profile(self):
        self.B = []
        self.t = []
        self.seg_k = []
        self.length = 0
        self.num_points = len(self.segs)*self.res
        if self.segs is not None:
            for index, current in enumerate(self.segs):
                current.update()
                current.calc_curve()
                self.B.extend(current.B)
                self.t.extend(current.t_a)
                self.seg_k.extend(np.multiply(np.ones(len(current.B), dtype=np.int8), index))
                self.length = self.length + current.length
        if not self.start_end_lock_x:
            self.start_point[0] = self.segs[0].p0.point[0]
        if not self.start_end_lock_y:
            self.start_point[1] = self.segs[0].p0.point[1]
        if not self.start_end_lock_x:
            self.end_point[0] = self.segs[len(self.segs)-1].p3.point[0]
        if not self.start_end_lock_y:
            self.end_point[1] = self.segs[len(self.segs)-1].p3.point[1]

    def update_profile_dx(self):
        self.length = 0
        if self.segs is not None:
            for current in self.segs:
                current.update()
                current.calc_curve_c_dx()
                self.length = self.length + current.length
        if not self.start_end_lock_x:
            self.start_point[0] = self.segs[0].p0.point[0]
        if not self.start_end_lock_y:
            self.start_point[1] = self.segs[0].p0.point[1]
        if not self.start_end_lock_x:
            self.end_point[0] = self.segs[len(self.segs)-1].p3.point[0]
        if not self.start_end_lock_y:
            self.end_point[1] = self.segs[len(self.segs)-1].p3.point[1]

    def save_control_points(self):
        """
        This class is responsible for saving the current velocity profile
        so that is can be loaded later in a new session. A new text file will be created
        in the sim_profiles folder specified name that will contain.
        The data the profile was created
        the time of profile (time or percent)
        If time based shoot duration otherwise None
        Number of segments that make up the profile
        location of each control point
        :param profile_name:
        :return:
        """
        data = {}
        data['curves'] = []
        for index, current in enumerate(self.segs):
            data['curves'].append({
                'type' : 'cubic_bezier',
                'control_points' : [
                    list(current.p0.point),
                    list(current.p1.point),
                    list(current.p2.point),
                    list(current.p3.point)
                ]
            })


        return data

    def load_text_profile(self, data):
        self.clear_all()
        num_segs = len(data["curves"])
        for i in range(0,int(num_segs)):
            self.add_curve()
            current = self.segs[i]
            current.p0.point = list(data['curves'][i]['control_points'][0])
            current.p1.point = list(data["curves"][i]['control_points'][1])
            current.p2.point = list(data["curves"][i]['control_points'][2])
            current.p3.point = list(data["curves"][i]['control_points'][3])
        self.update_profile()
