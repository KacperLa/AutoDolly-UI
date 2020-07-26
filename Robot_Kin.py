import numpy as np
import math
import pygame
from theme_AD import *



vertex = [0, 0, 0, 1]


class Robot:
    def __init__(self, body_length=50, center=None, body_angle=0, wheel_angle=0):
        # Initilize robot at starting positon
        if center is None:
            center = vertex
        self.center = center
        self.body_angle = body_angle
        self.camera_angle = 0
        self.wheel_angle = wheel_angle
        self.body_length = body_length

        self.corner_1 = [self.center[0] - self.body_length / 2,
                         self.center[1] - ((self.body_length / 2) * math.atan(math.radians(30)))]
        self.corner_2 = [self.center[0] + self.body_length / 2,
                         self.center[1] - ((self.body_length / 2) * math.atan(math.radians(30)))]
        self.corner_3 = [self.center[0], self.center[1] + ((self.body_length / 2) * math.atan(math.radians(30)))]

        self.c_corner_1 = (0, 0, 0, 1)
        self.c_corner_2 = (0, 0, 0, 1)
        self.c_corner_3 = (0, 0, 0, 1)

        self.wheel_1 = Module(wheel_angle)
        self.wheel_2 = Module(wheel_angle)
        self.wheel_3 = Module(wheel_angle)

    def KIN_MODEL(self, theta, w, v):
        w = w * 1
        v_x = v * math.cos(theta)
        v_y = v * math.sin(theta)
        w_x_1 = w * math.cos(-math.pi / 6.0)
        w_y_1 = w * math.sin(-math.pi / 6.0)
        w_x_2 = -w * math.cos(math.pi / 6.0)
        w_y_2 = -w * math.sin(math.pi / 6.0)
        w_x_3 = w * math.cos(math.pi / 2.0)
        w_y_3 = w * math.sin(math.pi / 2.0)
        x_1 = v_x + w_x_1
        y_1 = v_y + w_y_1
        x_2 = v_x + w_x_2
        y_2 = v_y + w_y_2
        x_3 = v_x + w_x_3
        y_3 = v_y + w_y_3

        angle_1 = math.atan2(x_1, y_1)
        if angle_1 < 0.0:
            angle_1 = angle_1 + 2.0 * math.pi

        angle_2 = math.atan2(x_2, y_2)
        if angle_2 < 0:
            angle_2 = angle_2 + 2.0 * math.pi

        angle_3 = math.atan2(x_3, y_3)
        if angle_3 < 0:
            angle_3 = angle_3 + 2.0 * math.pi

        angle_1 = angle_1  # top left
        angle_2 = angle_2  # top right
        angle_3 = angle_3  # bottom

        v_1 = math.sqrt(pow(x_1, 2) + pow(y_1, 2))
        v_2 = math.sqrt(pow(x_2, 2) + pow(y_2, 2))
        v_3 = math.sqrt(pow(x_3, 2) + pow(y_3, 2))

        return [[angle_1,angle_2,angle_3],[v_1,v_2,v_3]]

    def update_modules(self, theta, w, v):

        angle, v = self.KIN_MODEL(theta, w, v)

        angle_1, angle_2, angle_3 = angle
        v_1, v_2, v_3 = v

        self.wheel_1.update_angle(angle_1, self.corner_1, v_1)
        self.wheel_2.update_angle(angle_2, self.corner_2, v_2)
        self.wheel_3.update_angle(angle_3, self.corner_3, v_3)

    def update_body(self, angle=0, x=0, y=0):
        self.center = [0, 0, 0, 0, 1]
        self.body_angle = angle
        hypo = math.sqrt(math.pow(self.body_length/2,2)+math.pow(self.body_length,2))
        self.corner_1 = [self.center[0] - self.body_length / 2,
                         self.center[1] - ((hypo) * math.asin(math.pi/6))/2]
        self.corner_2 = [self.center[0] + self.body_length / 2,
                         self.center[1] - ((hypo) * math.asin(math.pi/6))/2]
        self.corner_3 = [self.center[0], self.center[1] + ((hypo) * math.asin(math.pi/6))]

        self.corner_1 = transform(self.body_angle, 0, 0, 0, self.corner_1)
        self.corner_2 = transform(self.body_angle, 0, 0, 0, self.corner_2)
        self.corner_3 = transform(self.body_angle, 0, 0, 0, self.corner_3)
        self.corner_1 = transform(0, x, y, 0, self.corner_1)
        self.corner_2 = transform(0, x, y, 0, self.corner_2)
        self.corner_3 = transform(0, x, y, 0, self.corner_3)

    def update_camera(self, angle=0, x=0, y=0):
        self.center = [0, 0, 0, 0, 1]
        self.camera_angle = -angle
        camera_length = 20
        hypo = math.sqrt(math.pow(camera_length / 2, 2) + math.pow(camera_length, 2))
        self.c_corner_1 = (self.center[0], self.center[1])
        self.c_corner_2 = (self.center[0] + (hypo * math.asin(math.pi / 6)), self.center[1] + (camera_length / 2))
        self.c_corner_3 = (self.center[0] + (hypo * math.asin(math.pi / 6)), self.center[1] - (camera_length / 2))

        self.c_corner_1 = transform(self.camera_angle, 0, 0, 0, self.c_corner_1)
        self.c_corner_2 = transform(self.camera_angle, 0, 0, 0, self.c_corner_2)
        self.c_corner_3 = transform(self.camera_angle, 0, 0, 0, self.c_corner_3)
        self.c_corner_1 = transform(0, x, y, 0, self.c_corner_1)
        self.c_corner_2 = transform(0, x, y, 0, self.c_corner_2)
        self.c_corner_3 = transform(0, x, y, 0, self.c_corner_3)

    def build_wheels(self, screen):
        seg_1 = self.wheel_1.wheel_points
        seg_2 = self.wheel_2.wheel_points
        seg_3 = self.wheel_3.wheel_points
        segs = [seg_1, seg_2, seg_3]
        for line in segs:
            pygame.draw.line(screen, RED, line[0], line[1], 5)

        seg_4 = self.wheel_1.arrow_points
        seg_5 = self.wheel_2.arrow_points
        seg_6 = self.wheel_3.arrow_points
        Arrows = [seg_4, seg_5, seg_6]
        for line in Arrows:
            pygame.draw.line(screen, GREEN, line[0], line[1], 5)

    def build_body(self, screen):
        pointlist = ((self.corner_1[0], self.corner_1[1]),(self.corner_2[0], self.corner_2[1]),(self.corner_3[0], self.corner_3[1]))
        pygame.draw.polygon(screen,BLACK,pointlist,3)

    def build_camera(self, screen):
        pointlist = ((self.c_corner_1[0],self.c_corner_1[1]),(self.c_corner_2[0],self.c_corner_2[1]),(self.c_corner_3[0],self.c_corner_3[1]))
        pygame.draw.polygon(screen,BLACK,pointlist,2)


class Module:
    def __init__(self, angle=0):
        self.angle_world = angle
        self.wheel = [[10, 0], [-10, 0]]
        self.arrow = [[10, 0], [-10, 0]]
        self.wheel_points = [[10, 0], [-10, 0]]
        self.arrow_points = [[10, 0], [-10, 0]]

    def update_angle(self, angle=0, pos=None, velocity=0):
        if pos is None:
            pos = [0, 0]
        self.velocity = velocity
        self.arrow = [[0, 0], [velocity * 100, 0]]
        self.angle = angle
        self.x = pos[0]
        self.y = pos[1]
        point_1 = transform(self.angle, 0, 0, 0, self.wheel[0])
        point_2 = transform(self.angle, 0, 0, 0, self.wheel[1])
        point_1 = transform(0, self.x, self.y, 0, point_1)
        point_2 = transform(0, self.x, self.y, 0, point_2)
        self.wheel_points = [point_1, point_2]

        point_3 = transform(self.angle, 0, 0, 0, self.arrow[0])
        point_4 = transform(self.angle, 0, 0, 0, self.arrow[1])
        point_3 = transform(0, self.x, self.y, 0, point_3)
        point_4 = transform(0, self.x, self.y, 0, point_4)
        self.arrow_points = [point_3, point_4]


def transform(q=0, x=0, y=0, z=0, element=False):
    def rotation(q=0):
        r_m = [[math.cos(q), (math.sin(q) * -1), 0, 0], [math.sin(q), math.cos(q), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        return (r_m)

    def translation(x=0, y=0, z=0):
        t_m = [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]
        return (t_m)

    r = rotation(q)
    t = translation(x, y, z)
    c = np.dot(r, t)
    if not element:
        return (c)
    else:
        a, b, c, d = np.dot(c, [element[0], element[1], 0, 1])
        return ([a, b])


