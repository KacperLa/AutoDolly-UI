import pygame
import numpy as np
from BazierConroller import BazierController
from theme_AD import *
from scipy.integrate import trapz


class Velocity_Profile():
    def __init__(self, window=None, font=None):
        self.y_max = 1
        self.shot_length = 0
        self.shot_time = 0
        self.points = None
        self.data_t = None
        self.data_v = None
        self.data_dis = None
        self.data_pc = None
        self.current_dis = None
        self.current_percent = None
        self.current_vel = None
        self.B_c_dx = None

        self.window = window
        if self.window is not None:
            self.start_point = [0, 0]
            self.end_point = [100, 0]
            self.draw_scale = [self.window.width/100, -self.window.height/1]
            self.myfont = font
            self.Curve = BazierController(self.window,self.start_point,self.end_point, True, True, self.draw_scale)
            self.start_v = 0
            self.end_v = 0
            self.Curve.add_curve()
            self.Curve.segs[0].p3.point = ([self.start_point[0] + (self.end_point[0] - self.start_point[0]) / 3, self.y_max + (self.start_point[1] - self.y_max) / 2])
            self.Curve.segs[0].p3.update()
            self.Curve.segs[0].reset()
            self.Curve.add_curve()
            self.Curve.segs[1].p3.point = ([self.start_point[0] + 2 * (self.end_point[0] - self.start_point[0]) / 3, self.y_max + (self.start_point[1] - self.y_max) / 2])
            self.Curve.segs[1].p3.update()
            self.Curve.segs[1].reset()
            self.Curve.add_curve()
            self.Curve.update_profile()
        else:
            self.Curve = BazierController()



    def draw(self, screen):
        self.Curve.draw(screen)

    def click(self, mouse):
        self.Curve.click(mouse)

    def adjust(self, mouse):
        self.Curve.adjust(mouse)

    def release(self):
        self.Curve.release()

    def update_profile(self):
        self.Curve.update_profile()

    def gen_profile(self, t):
        if self.Curve.segs is not None:
            self.data_t = []  # time data
            self.data_v = []  # velocity data
            self.data_dis = []  # Distance traveled data
            self.data_pc = []  # Percent Completion data
            self.shot_time = t  # shot duration
            self.shot_length = 0  # shot length
            data_x = []
            data_y = []
            self.Curve.update_profile()
            x_scale = t / 100
            dp = 1 / (len(self.Curve.segs) * 100)

            _last_p = 0
            with open('Velocity Profile.txt', 'w') as vpf:
                for num_thing, current in enumerate(self.Curve.segs):
                    for xy in current.B:
                        x, y = xy
                        y = y
                        x = x * x_scale
                        data_x.append(x)
                        data_y.append(y)
                        dis = trapz(data_y, data_x)
                        _last_p = _last_p + dp
                        self.data_t.append(round(x, 5))
                        self.data_v.append(y/100)
                        self.data_dis.append(dis)
                        self.data_pc.append(_last_p)
                        vpf.write(str(x) + ", " + str(y) + ", " + str(dis) + ", " + str(_last_p) + "\n")
        max_dis = max(self.data_dis)
        print(self.shot_length, max_dis)

    def gen_p_c_profile(self, d):
        """
        Generates a self.B array from a percent completion graph
        The way this function works is as follows, the input variable d represents the total distance to be traveled
        by the dolly, this variable is divided by the total number of velocity data points available. The number of
        velocity data points is obtained by adding up the self.res variable from each segment. This then gives us the dx
        for every velocity point by dividing this dx by the velocity value for that particular instant gives the dt for
        that particular instant.
        :param d: Total distance to be traveled by the dolly
        :return:  Velocity profile in the time domain
        """
        self.data_t = []  # time data
        self.data_v = []  # velocity data
        self.data_dis = []  # Distance traveled data
        self.data_pc = []  # Percent Completion data
        self.shot_time = 0  # shot duration
        self.shot_length = d  # shot length
        data_x = []
        data_y = []
        self.Curve.update_profile_dx()

        y_scale = .05
        dx = self.shot_length / (len(self.Curve.segs)*100)
        dp = 1 / (len(self.Curve.segs)*100)

        _last_t = 0
        _last_p = 0
        _last_d = 0
        dt = 0
        for num_thing, current in enumerate(self.Curve.segs):
            for xy in current.B_c_dx:
                _, y = xy
                v = y*y_scale
                if v == 0:
                    dt = 0
                else:
                    dt = (dx/(v*100))
                _last_t = _last_t + dt
                _last_p = _last_p + dp
                _last_d = _last_d + dx
                dis = _last_d
                self.data_t.append(round(_last_t,5))
                self.data_v.append(v)
                self.data_dis.append(dis)
                self.data_pc.append(_last_p)

        self.shot_time = max(self.data_t)
        print("time data: ", self.data_t)
        max_dis = max(self.data_dis)
        print(self.shot_length, max_dis)

    def interp_data_per_t(self, c_t):
        """
        self.data_t ascending 1-D array of time points
        self.data_dis 1-D array of distance at respective time point

        :param c_t: point to be interpolated with in self.data t
        :return:    interpolated distance value for requested time point
        """
        ass_check = np.all(np.diff(self.data_t) >= 0)
        #  diff = np.diff(self.data_t)
        #  print(self.data_t)
        #  print(diff)
        self.current_dis = np.interp(c_t,self.data_t, self.data_dis)
        self.current_percent = np.interp(c_t,self.data_t, self.data_pc)
        self.current_vel = np.interp(c_t,self.data_t, self.data_v)
        #print(c_t, ass_check)
        return self.current_dis , self.current_vel, self.current_percent
