import pygame
import math
import numpy as np
import os
import time
import json
import socketio
import copy
from UI_Elements import *
from Robot_Kin import *
from Velocity_Planning import Velocity_Profile
from Position_Planning import Position_Controller
from Theta_Controller import Theta_Profile
from theme_AD import *

# Set the width and height of the screen [width,height]
size = [1250, 510]
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
pygame.display.set_caption("Auto Dolly")
pygame.mouse.set_visible(1)

myfont = pygame.font.SysFont('Arial',12)

# defining canter of window
Height = size[1] - 20
Width = size[0]

center = [Width / 6, Height / 4, 0, 1]

info_w = grid(250, 500, (0, 0), 40)
velocity_w = grid(500, 250, (750, 250), 40)
velocity_p_w = grid(velocity_w.x_w * 36, velocity_w.y_w * 31, velocity_w(2.5, 6), 40)
pos_w = grid(500, 500, (250, 0), 40)
pos_p_w = grid(pos_w.x_w * 35.5, pos_w.y_w * 35.5, pos_w(3, 3), 40)
theta_w = grid(500, 250, (750, 0), 40)
theta_p_w = grid(theta_w.x_w * 36, theta_w.y_w * 31, theta_w(2.5, 6), 40)

# initilize socketIO
sio = socketio.Client()
dolly_connection = False
dolly_state = None
bus_voltage = None
dolly_settings = None
recived_pose = None


@sio.on('status')
def on_message(data):
    print(data)


@sio.on('pose')
def on_message(data):
    global  recived_pose
    recived_pose = data['pose']
    print("Robot Pose: ", recived_pose)


@sio.event
def connect():
    global dolly_connection
    dolly_connection = True
    print("I'm connected!")


@sio.event
def disconnect():
    global dolly_connection
    dolly_connection = False
    print("Connection ended by server")


def connect_dolly():
    global dolly_connection
    try:
        sio.connect('http://10.0.0.206:8080')
        dolly_state = True
    except IOError:
        print("Connection Failed")
        dolly_state = False


def disconnect_dolly():
    global dolly_connection
    try:
        sio.emit("STATE_PUSH", "IDLE")
        sio.disconnect()
        dolly_connection = False

    except IOError:
        print("Failed to Run disconnect command")


def change_dolly_state(requested_state):
    try:
        msg = {
            'requested_state': requested_state,
        }
        print(msg)
        sio.emit('status', msg)
    except IOError:
        print("Failed to send state change command")


def send_data(a_v, a_w, v):
    global dolly_state
    packet = {
        'dolly': {
            'velocity': 0,
            'theta': 0,
            'omega_dot': 0,
        },
        'pedestal': {
            'z_dot': 0,
        },
    }
    try:
        if True:
            packet['dolly']['velocity'] = v
            packet['dolly']['theta'] = a_v
            packet['dolly']['omega_dot'] = a_w
            #print(packet)
            sio.emit("command", packet)

    except IOError:
        print("Failed to send command packet")


def send_path_to_dolly(data):
    global dolly_connection
    if dolly_connection:
        sio.emit("path", data)


def send_timer_state(data):
    global  dolly_connection
    if dolly_connection:
        sio.emit("timer", data)


class Tracker():
    def __init__(self):
        self.rel_dolly = Robot(20)
        # self.rel_dolly_2 = Robot(20)
        self.pos = None
        self.pos_n = None
        self.r_pos = None
        self.draw_pos = None
        # self.draw_pos_2 = None
        self.cor = None
        # self.pos_offset = [0, 0, 0]


    def uupdate_pos(self, rel_pos, UI_orgin, UI_scale):
        self.pos = rel_pos
        self.r_pos = -rel_pos[2] + math.pi/2
        # self.pos_n = np.reshape(np.dot(transform(self.pos_offset[2], -self.pos_offset[0], -self.pos_offset[1]),([[self.pos[0]],[self.pos[1]],[0],[1]])),(1,-1))[0]
        # print(self.pos_n)
        # self.r_pos_n =  self.r_pos + self.pos_offset[2]
        self.draw_pos = np.add(np.multiply([self.pos[0], self.pos[1]], UI_scale), UI_orgin)
        # self.draw_pos_2 = np.add(np.multiply([self.pos_n[0], self.pos_n[1]], UI_scale), UI_orgin)

    def draw(self, screen):
        # self.rel_dolly_2.update_camera(self.r_pos_n, self.draw_pos_2[0], self.draw_pos_2[1])
        # pygame.draw.circle(screen, BLUE, [int(self.draw_pos_2[0]), int(self.draw_pos_2[1])], 5)
        # self.rel_dolly_2.build_camera(screen)

        self.rel_dolly.update_camera(self.r_pos, self.draw_pos[0], self.draw_pos[1])
        pygame.draw.circle(screen, RED, [int(self.draw_pos[0]), int(self.draw_pos[1])], 5)
        self.rel_dolly.build_camera(screen)

    def update_start_pos(self):
        self.pos_offset = copy.copy(self.pos)

class draw_bg():
    def __init__(self):
        #  Backgrounds
        self.b_g = pygame.Surface(size)
        self.b_g.fill(BACKGROUND)

        v_p = velocity_p_w.space
        p_p = pos_p_w.space  # Position Area
        ani_g = theta_p_w.space
        info_p = info_w.space

        backgrounds = [info_p, v_p, p_p, ani_g]
        bk_colors = [GRAY_3, GRAY_2, GRAY_2, GRAY_2]
        #  Draw all Backgrounds
        for c, bg in zip(bk_colors, backgrounds):
            pygame.draw.rect(self.b_g, c, bg)

        dev_num_v = 10
        for i in range(0, dev_num_v + 1):
            pygame.draw.line(self.b_g, UI_S, velocity_p_w(i * (40 / dev_num_v), 0),
                             velocity_p_w(i * (40 / dev_num_v), 40), 1)
            pygame.draw.line(self.b_g, UI_S, velocity_p_w(0, i * (40 / dev_num_v)),
                             velocity_p_w(40, i * (40 / dev_num_v)), 1)

        p_t = myfont.render("Path Data:", 1, TEXT_light)
        self.b_g.blit(p_t, info_w(1, .5))

        r_t = myfont.render("Remote Connection:", 1, TEXT_light)
        self.b_g.blit(r_t, info_w(1, 15))

        d_t = myfont.render("Tuning Parameters:", 1, TEXT_light)
        self.b_g.blit(d_t, info_w(1, 25))

        # Info text
        v_p = myfont.render("Velocity Profile", 1, TEXT_light)
        s_t = myfont.render("Simulation Time: ", 1, TEXT_light)

        self.b_g.blit(v_p, velocity_w(1, 1))
        self.b_g.blit(s_t, theta_w(3, 1))

        v_t = myfont.render("1", 1, TEXT_light)
        v_m = myfont.render(".5", 1, TEXT_light)
        v_b = myfont.render("0", 1, TEXT_light)

        self.b_g.blit(v_t, velocity_w(1.25, 5))
        self.b_g.blit(v_m, velocity_w(1.25, 20))
        self.b_g.blit(v_b, velocity_w(1.25, 36))

        s_d = myfont.render("Type:", 1, TEXT_light)
        self.b_g.blit(s_d, info_w(1, 6.2))
        t_d = myfont.render("Duration:", 1, TEXT_light)
        self.b_g.blit(t_d, info_w(20, 6.2))


        Heading_0 = myfont.render("Vel", 1, TEXT_light)
        Heading_0_1 = myfont.render("Theta", 1, TEXT_light)
        Heading_0_2 = myfont.render("Pos", 1, TEXT_light)
        Heading_0_3 = myfont.render("Rot", 1, TEXT_light)

        Heading_1 = myfont.render("Z:", 1, TEXT_light)
        subHeading_1 = myfont.render("P:", 1, TEXT_light)
        subHeading_2 = myfont.render("I:", 1, TEXT_light)
        subHeading_3 = myfont.render("D:", 1, TEXT_light)
        subHeading_4 = myfont.render("F:", 1, TEXT_light)

        Heading_3 = myfont.render("A: ", 1, TEXT_light)
        Heading_4 = myfont.render("B:", 1, TEXT_light)
        subHeading_5 = myfont.render("kp:", 1, TEXT_light)
        subHeading_6 = myfont.render("kv:", 1, TEXT_light)
        subHeading_7 = myfont.render("ki:", 1, TEXT_light)

        self.b_g.blit(Heading_0, info_w(4, 26.5))
        self.b_g.blit(Heading_0_2, info_w(24, 26.5))
        self.b_g.blit(Heading_0_1, info_w(13, 26.5))
        self.b_g.blit(Heading_0_3, info_w(34, 26.5))

        self.b_g.blit(Heading_1, info_w(21, 28))
        self.b_g.blit(subHeading_1, info_w(21, 30))
        self.b_g.blit(subHeading_2, info_w(21, 32))
        self.b_g.blit(subHeading_3, info_w(21, 34))
        self.b_g.blit(subHeading_4, info_w(21, 36))
        self.b_g.blit(Heading_3, info_w(.5, 28))
        self.b_g.blit(Heading_4, info_w(.5, 30))
        self.b_g.blit(subHeading_5, info_w(.5, 32))
        self.b_g.blit(subHeading_6, info_w(.5, 34))
        self.b_g.blit(subHeading_7, info_w(.5, 36))

    def __call__(self, screen):
        screen.blit(self.b_g, (0, 0))


def constrain(x, min, max):
    if x > max:
        o = max
    elif x < min:
        o = min
    else:
        o = x
    return o


class Dynamics:
    def update_pidf(self, data):
        self.deadzone = data['position']['dead_zone']
        self.P_gain = data['position']['p']
        self.I_gain = data['position']['i']
        self.D_gain = data['position']['d']
        self.FF = data['position']['f']

        self.rot_deadzone = data['rotation']['dead_zone']
        self.rot_P_gain = data['rotation']['p']
        self.rot_I_gain = data['rotation']['i']
        self.rot_D_gain = data['rotation']['d']
        self.rot_FF = data['rotation']['f']

    def update_data(self):
        self.start_point = [self.p_c.Curve.start_point[0], self.p_c.Curve.start_point[1], 0]
        self.path_length = self.p_c.Curve.length

    def update_sim_pos(self, c_t):
        self.dis_new, self.vel_new, perc_new = self.v_c.interp_data_per_t(c_t)
        self.sim_rot = -self.t_c.get_a_for_t(self.p_c.current_seg, self.p_c.current_t) + math.pi/2
        self.sim_pos = self.p_c.find_xya_per_dis(self.dis_new)
        print("Dolly pos a :", self.sim_pos)
        print("Dolly rot: ", self.sim_rot)

    def draw(self, screen):
        _pos = self.p_c.draw_current_pos
        if self.sim_pos is not None and self.sim_rot is not None:
            pygame.draw.circle(self.p_c.b_g, RED, [int(_pos[0]), int(_pos[1])], 5)
            self.sim_dolly.update_camera(self.sim_rot, _pos[0], _pos[1])
            self.sim_dolly.build_camera(self.p_c.b_g)

        if self.path_length is None:
            self.path_length = 0
        if self.dis_new is None:
            self.dis_new = 0
        p_l = myfont.render("Path Length: " + str(round(self.path_length , 2)) + " m", 1, TEXT_light)
        c_l = myfont.render("Distance Along Path: " + str(round(self.dis_new , 2)) + " m", 1, TEXT_light)
        screen.blit(p_l, info_w(2, 10))
        screen.blit(c_l, info_w(2, 11.5))

        if self.sim_pos is not None:
            # Draw requested position
            _pos = self.p_c.draw_current_pos
            pygame.draw.circle(self.p_c.b_g, RED, [int(_pos[0]), int(_pos[1])], 5)
            # Draw Facing Direction
            if self.sim_rot is not None:
                self.sim_dolly.build_camera(self.p_c.b_g)

                # Draw Heading
                x_h = self.vel_new * 100 * math.cos(self.sim_rot)
                y_h = self.vel_new * 100 * math.sin(self.sim_rot)
                pygame.draw.line(self.p_c.b_g, BLACK, [int(self.sim_pos[0]), int(self.sim_pos[1])],
                                 [int(self.sim_pos[0]) + x_h, int(self.sim_pos[1]) + y_h], 5)

            # Draw dead zone
            pygame.draw.circle(self.p_c.b_g, BLACK, [int(self.sim_pos[0]), int(self.sim_pos[1])], int(round(self.deadzone))+1,1)

        # Draw Error Line
        if self.sim_pos is not None and self.rel_pos is not None:
            pygame.draw.line(screen, RED, [self.sim_pos[0], self.sim_pos[1]], [self.rel_pos[0], self.rel_pos[1]], 2)

        # Draw Path

    def calc_error(self):
        if self.sim_rot is not None and self.rel_rot is not None:
            self.error_rot = self.sim_rot - self.rel_rot
            self.error_rot_int = self.error_rot_int + self.error_rot
            if abs(self.error_rot) < self.rot_deadzone:
                self.error_rot = 0
                self.error_rot_int = 0
        if self.sim_pos is not None and self.rel_pos is not None:

            self.error_x = self.sim_pos[0] - self.rel_pos[0]
            self.error_x_int = constrain((self.error_x_int + self.error_x), -.5, .5)

            self.error_y = self.sim_pos[1] - self.rel_pos[1]
            self.error_y_int = constrain((self.error_y_int + self.error_y), -.5, .5)

            if abs(self.error_x_int) >= .2 or abs(self.error_y_int >= .2):
                pass
                # print("hitting max int x ", self.error_x_int, "  y  ", self.error_y_int)

            if (math.sqrt(math.pow(self.error_x, 2) + math.pow(self.error_y, 2))) < self.deadzone:
                self.error_x = 0
                self.error_y = 0
                #  self.error_x_int = 0
                #  self.error_y_int = 0

            if (math.sqrt(math.pow(self.error_x, 2) + math.pow(self.error_y, 2))) < .3:
                self.tracking = True
            else:
                self.tracking = False

        if self.vel_new is not None:
            x_signal_FF = self.vel_new * self.FF * math.cos(self.sim_rot)
            y_signal_FF = self.vel_new * self.FF * math.sin(self.sim_rot)

            # Calculating X
            self.x_signal = self.P_gain * self.error_x + self.I_gain * self.error_x_int + x_signal_FF
            # Calculating Y
            self.y_signal = self.P_gain * self.error_y + self.I_gain * self.error_y_int + y_signal_FF
            # calculating W
            self.w_signal = float(self.rot_P_gain * self.error_rot + self.rot_I_gain * self.error_rot_int)
        else:
            # Calculating X
            self.x_signal = self.P_gain * self.error_x + self.I_gain * self.error_x_int
            # Calculating Y
            self.y_signal = self.P_gain * self.error_y + self.I_gain * self.error_y_int
            # calculating W
            self.w_signal = float(self.rot_P_gain * self.error_rot + self.rot_I_gain * self.error_rot_int)

        v = math.sqrt(math.pow(self.x_signal, 2) + math.pow(self.y_signal, 2))
        a = math.atan2(self.x_signal, self.y_signal) + self.rel_pos[2]
        w = constrain(self.w_signal, -1, 1)
        return v, a, w

    def __init__(self):
        self.start_point = None
        self.path_length = None

        self.plan_mode = "Rec-path"
        self.velocity_type = "Time"

        self.v_c = Velocity_Profile(velocity_p_w, myfont)
        self.p_c = Position_Controller(pos_p_w)
        self.t_c = Theta_Profile(theta_p_w, myfont)
        self.sim_dolly = Robot(20)

        self.tracking = False
        self.vel_new = None
        self.dis_new = None
        self.sim_pos = None
        self.sim_rot = None
        self.rel_pos = None
        self.rel_rot = None
        self.error_x = 0
        self.error_x_int = 0
        self.error_y = 0
        self.error_y_int = 0
        self.error_rot = 0
        self.error_rot_int = 0
        self.deadzone = 1
        self.rot_deadzone = .2

        self.P_gain = .02
        self.I_gain = 0
        self.D_gain = 1
        self.FF = 0
        self.rot_P_gain = 0
        self.rot_I_gain = 0
        self.rot_D_gain = 0
        self.rot_FF = 0

        self.x_signal = 0
        self.y_signal = 0
        self.w_signal = 0
        self.x = 0
        self.y = 0
        self.angle = 0
        self.sim_index = None
        self.shot_time = None

    def update_con(self, angle_v, angle_r, velocity):
        a_v = angle_v
        a_r = angle_r
        x = math.sin(angle_v)
        y = 0
        return a_v, a_r, x, y

    def adjust_path(self, mouse_g):
        if self.v_c.Curve.moving:
            self.v_c.adjust(mouse_g)

        if self.p_c.Curve.moving:
            self.p_c.adjust(mouse_g)

        if self.t_c.Curve.moving:
            self.t_c.adjust(mouse_g)

    def add_key_frame(self):
        self.t_c.add_curve_at_cur()
        self.p_c.add_curve_at_cur()

    def reset_pos(self):
        """
        Purpose: Return simulated dolly to start position
        """
        if self.start_point is not None:
            self.sim_pos = self.start_point


def main():
    global recived_pose, dolly_state, dolly_connection
    back_ground = draw_bg()
    dynamics = Dynamics()
    tracker = Tracker()

    odrive_par = {
        "dolly": {
            "velocity_limit": 0,
            "omega_dot_limit": 0,
            "module": {
                "theta": {
                    "velocity_limit": 0,
                    "current_limit": 0,
                    "bandwidth": 0,
                    "k_p": 0,
                    "k_v": 0,
                    "k_vi": 0
                },
                "velocity": {
                    "velocity_limit": 0,
                    "current_limit": 0,
                    "bandwidth": 0,
                    "k_v": 0,
                    "k_vi": 0
                }
            }
        },
        "pedestal": {
            "z": {
                "velocity_limit": 0,
                "current_limit": 0,
                "k_v": 0,
                "k_vi": 0
            }
        }
    }

    # import Settings
    settings_file_name = "AD_CONFIG.json"
    settings_file = os.path.join(os.getcwd(), settings_file_name)
    with open(settings_file, "r") as config_file:
        config = json.load(config_file)
        dynamics.deadzone = config["pos_pidf"]["position"]["dead_zone"]
        dynamics.P_gain = config["pos_pidf"]["position"]["p"]
        dynamics.I_gain = config["pos_pidf"]["position"]["i"]
        dynamics.D_gain = config["pos_pidf"]["position"]["d"]
        dynamics.FF = config["pos_pidf"]["position"]["f"]
        dynamics.rot_deadzone = config["pos_pidf"]["rotation"]["dead_zone"]
        dynamics.rot_P_gain = config["pos_pidf"]["rotation"]["p"]
        dynamics.rot_I_gain = config["pos_pidf"]["rotation"]["i"]
        dynamics.rot_D_gain = config["pos_pidf"]["rotation"]["d"]
        dynamics.rot_FF = config["pos_pidf"]["rotation"]["f"]
        odrive_par["dolly"] = config["dolly"]

    # Button deceleration
    # =========================================
    return_home_bt = Button(pos_w(3, .5), False, pos_w.x_w * 8, pos_w.y_w * 2, UI_EH, True, myfont, "Return Home")
    connect_bt = Button(info_w(29, 16.5), False, info_w.x_w * 10, info_w.y_w * 1.5, UI_EH, True, myfont, "Connect", "Disconnect")
    send_path_bt = Button(info_w(1, 8), False, info_w.x_w * 18, info_w.y_w * 1.5, UI_EH, True, myfont, "Send Path Data")
    idle_bt = Button(info_w(29, 18.5), False, info_w.x_w * 10, pos_w.y_w * 1.5, UI_EH, True, myfont, "Enter", "Disable")
    remote_start_bt = Button(info_w(0, 23), False, info_w.x_w * 40/3, info_w.y_w * 1.5, UI_EH, True, myfont, "AD Start")
    remote_stop_bt = Button(info_w(40/3, 23), False, info_w.x_w * 40/3, info_w.y_w * 1.5, UI_EH, True, myfont, "AD Stop")
    remote_rev_bt = Button(info_w(80/3, 23), False, info_w.x_w * 40/3, info_w.y_w * 1.5, UI_EH, True, myfont, "AD Rev")
    dump_errors_bt = Button(info_w(0, 21), False, info_w.x_w * 40/3, info_w.y_w * 1.5, UI_EH, True, myfont, "Dump Errors")
    update_start_bt = Button(info_w(40/3, 21), False, info_w.x_w * 40/3, info_w.y_w * 1.5, UI_EH, True, myfont, "Update Home")

    add_bezier_v = Button(velocity_w(30, 1), False, velocity_w.x_w * 8, velocity_w.y_w * 4, UI_EH, True, myfont,
                          "Split")
    Export_v_p = Button(info_w(19, 8), False, info_w.x_w * 20, info_w.y_w * 1.5, UI_EH, True, myfont, "Generate Path")

    start_bt = Button(pos_w(11.5, .5), False, pos_w.x_w * 6, pos_w.y_w * 2, UI_EH, False, myfont, "Start", "Pause")
    restart_bt = Button(pos_w(18.5, .5), False, pos_w.x_w * 6, pos_w.y_w * 2, UI_EH, True, myfont, "Reset")
    revers_bt = Button(pos_w(25.5, .5), False, pos_w.x_w * 6, pos_w.y_w * 2, UI_EH, True, myfont, "Reverse")
    add_key = Button(pos_w(32.5, .5), False, pos_w.x_w * 6, pos_w.y_w * 2, UI_EH, True, myfont, "Add Key")

    save_path_profile_bt = Button(info_w(29, 4), False, info_w.x_w * 10, info_w.y_w * 1.5, UI_EH, True, myfont, "Save")
    load_path_profile_bt = Button(info_w(29, 2), False, info_w.x_w * 10, info_w.y_w * 1.5, UI_EH, True, myfont, "Import")
    send_pos_pidf_bt = Button(info_w(40/2, 38), False, info_w.x_w * 40/2, info_w.y_w * 2, UI_EH, True, myfont,"Send PIDF")
    send_odrive_bt = Button(info_w(0, 38), False, info_w.x_w * 40/2, info_w.y_w * 2, UI_EH, True, myfont,"Send Odrive")

    # =========================================
    buttons = (remote_start_bt, remote_stop_bt, remote_rev_bt, connect_bt, send_path_bt, start_bt, restart_bt, idle_bt, revers_bt, add_bezier_v, add_key, Export_v_p, save_path_profile_bt, load_path_profile_bt,
    send_pos_pidf_bt, dump_errors_bt, update_start_bt, send_odrive_bt, return_home_bt)
    #  ========================================

    # Slider deceleration
    #  ========================================
    time_sl = Slider(velocity_w(3, 39.5), velocity_w(38.5, 39.5), Width)
    x_sl = Slider(pos_w(3, 39.5), pos_w(38.5, 39.5), Width)
    y_sl = Slider(pos_w(1, 38), pos_w(1, 1), Width, layout="y")

    #  ========================================
    sliders = [time_sl]
    #  ========================================

    # Textbox Declaration
    #  ========================================
    shot_time = InputBox(myfont, info_w(40 - 11, 6), info_w.x_w * 10, info_w.y_w * 1.5)
    path_name_txt = InputBox(myfont, info_w(1, 4), info_w.x_w * 28, info_w.y_w * 1.5, "Path Name")

    dz_in = InputBox(myfont, info_w(40 - 17, 28), info_w.x_w * 8, info_w.y_w * 1.5)
    p_in = InputBox(myfont, info_w(40 - 17, 30), info_w.x_w * 8, info_w.y_w * 1.5)
    i_in = InputBox(myfont, info_w(40 - 17, 32), info_w.x_w * 8, info_w.y_w * 1.5)
    d_in = InputBox(myfont, info_w(40 - 17, 34), info_w.x_w * 8, info_w.y_w * 1.5)
    f_in = InputBox(myfont, info_w(40 - 17, 36), info_w.x_w * 8, info_w.y_w * 1.5)
    rot_dz_in = InputBox(myfont, info_w(40 - 8, 28), info_w.x_w * 8, info_w.y_w * 1.5)
    rot_p_in = InputBox(myfont, info_w(40 - 8, 30), info_w.x_w * 8, info_w.y_w * 1.5)
    rot_i_in = InputBox(myfont, info_w(40 - 8, 32), info_w.x_w * 8, info_w.y_w * 1.5)
    rot_d_in = InputBox(myfont, info_w(40 - 8, 34), info_w.x_w * 8, info_w.y_w * 1.5)
    rot_f_in = InputBox(myfont, info_w(40 - 8, 36), info_w.x_w * 8, info_w.y_w * 1.5)

    ip_address = InputBox(myfont, info_w(1, 16.5), info_w.x_w * 28, info_w.y_w * 1.5)


    v_amp_lim = InputBox(myfont, info_w(3, 28), info_w.x_w * 8, info_w.y_w * 1.5, "0")
    v_band_lim = InputBox(myfont, info_w(3, 30), info_w.x_w * 8, info_w.y_w * 1.5, "0")
    v_pos_gain_in = InputBox(myfont, info_w(3, 32), info_w.x_w * 8, info_w.y_w * 1.5, "0")
    v_vel_gain_in = InputBox(myfont, info_w(3, 34), info_w.x_w * 8, info_w.y_w * 1.5, "0")
    v_vel_i_gain_in = InputBox(myfont, info_w(3, 36), info_w.x_w * 8, info_w.y_w * 1.5, "0")

    t_amp_lim = InputBox(myfont, info_w(40-28, 28), info_w.x_w * 8, info_w.y_w * 1.5, "0")
    t_band_lim = InputBox(myfont, info_w(40-28, 30), info_w.x_w * 8, info_w.y_w * 1.5, "0")
    t_pos_gain_in = InputBox(myfont, info_w(40-28, 32), info_w.x_w * 8, info_w.y_w * 1.5, "0")
    t_vel_gain_in = InputBox(myfont, info_w(40-28, 34), info_w.x_w * 8, info_w.y_w * 1.5, "0")
    t_vel_i_gain_in = InputBox(myfont, info_w(40-28, 36), info_w.x_w * 8, info_w.y_w * 1.5, "0")
    #  ========================================
    input_boxes = [ip_address, shot_time,path_name_txt, dz_in, p_in, i_in, d_in, f_in, rot_dz_in, rot_p_in, rot_i_in, v_amp_lim, v_band_lim, t_amp_lim, t_band_lim, rot_d_in, rot_f_in, v_pos_gain_in, v_vel_gain_in, v_vel_i_gain_in, t_pos_gain_in, t_vel_gain_in, t_vel_i_gain_in]
    #  ========================================

    # Dropdown Menu Declaration
    #  ========================================
    shot_type_list = ("Time", "Percent")
    states_list = ("disabled", "rail", "onboardmanual")
    states_load = Drop_Down(info_w(1, 18.5), info_w.x_w * 28, info_w.y_w * 1.5, UI_EH, True, myfont, states_list)
    velocity_type = Drop_Down(info_w(7, 6), info_w.x_w * 12, info_w.y_w * 1.5, UI_EH, True, myfont, shot_type_list)
    path_profile_list = os.listdir(os.path.join(os.getcwd(),"sim_paths"))
    path_profile_load = Drop_Down(info_w(1, 2), info_w.x_w * 28, info_w.y_w * 1.5, UI_EH, True, myfont, path_profile_list)
    #  ========================================
    drop_downs = [states_load, velocity_type, path_profile_load]
    #  ========================================

    dz_in.update(dynamics.deadzone)
    p_in.update(dynamics.P_gain)
    i_in.update(dynamics.I_gain)
    d_in.update(dynamics.D_gain)
    f_in.update(dynamics.FF)
    rot_dz_in.update(dynamics.rot_deadzone)
    rot_p_in.update(dynamics.rot_P_gain)
    rot_i_in.update(dynamics.rot_I_gain)
    rot_d_in.update(dynamics.rot_D_gain)
    rot_f_in.update(dynamics.rot_FF)
    v_pos_gain_in.update(str(odrive_par["dolly"]["module"]["velocity"]["k_p"]))
    v_vel_gain_in.update(str(odrive_par["dolly"]["module"]["velocity"]["k_v"]))
    v_vel_i_gain_in.update(str(odrive_par["dolly"]["module"]["velocity"]["k_vi"]))
    t_pos_gain_in.update(str(odrive_par["dolly"]["module"]["theta"]["k_p"]))
    t_vel_gain_in.update(str(odrive_par["dolly"]["module"]["theta"]["k_v"]))
    t_vel_i_gain_in.update(str(odrive_par["dolly"]["module"]["theta"]["k_vi"]))

    select_mode_v = False
    new_start_time = None
    time_run = False
    cur_time = 0
    cur_time_s = 0
    old_time = 0
    tab_state_1 = 0

    done = False
    while not done:
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            # if True in keys:
            #     print(keys.index(True))
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # gets mouse position
                mouse_button = event.button
                dynamics.v_c.click(mouse_pos)
                dynamics.p_c.click(mouse_pos)
                dynamics.p_c.handle_event(event, mouse_pos, keys)
                dynamics.t_c.click(mouse_pos)
                dynamics.t_c.handle_event(event, mouse_pos, keys)
                for button in buttons:
                    if button.face.collidepoint(mouse_pos):
                        if button.not_done:
                            button.action()
                            button.not_done = False
                for slider in sliders:
                    slider.handle_event(event)

                if select_mode_v:
                    if v_p.collidepoint(mouse_pos):
                        for i, pt in enumerate(x_seg):
                            if i == 0:
                                pass
                            else:
                                if mouse_pos[0] > x_seg[i - 1] and mouse_pos[0] < x_seg[i]:
                                    dynamics.v_c.Curve.insert_curve(i - 1)
                                    add_bezier_v.color = UI_EH
                                    add_bezier_v.do = False
                                    select_mode_v = False

            for box in input_boxes:
                box.handle_event(event)

            for drop_down in drop_downs:
                drop_down.handle_event(event)

            if event.type == pygame.MOUSEBUTTONUP:
                dynamics.v_c.release()
                dynamics.p_c.release()
                dynamics.t_c.release()
                for button in buttons:
                    if not button.not_done:
                        button.not_done = True
                for slider in sliders:
                    slider.sliding = False

        mouse_g = pygame.mouse.get_pos()

        dynamics.adjust_path(mouse_g)
        dynamics.update_data()

        for slider in sliders:
            if slider.sliding:
                slider.adjust_value(mouse_g[0], mouse_g[1])

        try:
            dynamics.shot_time = float(shot_time.text)
        except:
            print("invalid shot duration")

        dynamics.velocity_type = velocity_type.value

        # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT

        if load_path_profile_bt.do:
            load_path_profile_bt.do = False
            try:
                with open(os.path.join(os.getcwd(), "sim_paths", path_profile_load.value),"r") as path_load_text:
                        data = json.load(path_load_text)
                        print(data)
                        dynamics.p_c.Curve.load_text_profile(data['position'])
                        dynamics.p_c.Curve.segs[0].p0.lock = True
                        dynamics.t_c.Curve.load_text_profile(data['omega'])
                        dynamics.v_c.Curve.load_text_profile(data['velocity'])
                        print("Profile Loaded")
            except IOError:
                print("Failed to load path")

        if save_path_profile_bt.do:
            save_path_profile_bt.do = False
            print("Saving path")
            data = {}
            data['name'] = path_name_txt.text
            data['duration'] = shot_time.text
            data['slam_id'] = "none"
            pos_dir = dynamics.p_c.Curve.save_control_points()
            theta_dir = dynamics.t_c.Curve.save_control_points()
            vel_dir = dynamics.v_c.Curve.save_control_points()
            data['position'] = pos_dir
            data['velocity'] = vel_dir
            data['omega'] = theta_dir
            print(data)
            cur_path = os.getcwd()
            file_path = os.path.join(cur_path, 'sim_paths', path_name_txt.text)
            with open((file_path + ".json"), 'w') as vpf:
                 json.dump(data, vpf)
            #path_profile_list = os.listdir(os.path.join(os.getcwd(), "sim_paths"))
            #path_profile_load.update_list(path_profile_list)

        if add_bezier_v.do:
            if dynamics.v_c.Curve.segs is not None:
                if not select_mode_v:
                    add_bezier_v.color = ORANGE
                    x_seg = [dynamics.v_c.Curve.segs[0].p0.draw_point[0], ]
                    for index, seg in enumerate(dynamics.v_c.Curve.segs):
                        x_seg.append(seg.p3.draw_point[0])
                    v_p = velocity_p_w.space
                    select_mode_v = True

        if add_key.do:
            add_key.do = False
            dynamics.add_key_frame()

        if Export_v_p.do:
            print(dynamics.p_c.Curve.B)
            print(dynamics.p_c.Curve.t)
            print(dynamics.p_c.Curve.seg_k)
            if dynamics.v_c.Curve.segs is not None:
                if velocity_type.value == "Time":
                    dynamics.v_c.gen_profile(int(shot_time.text))
                    print("TIme Based Velocity Profile Generated")
                elif velocity_type.value == "Percent":
                    dynamics.v_c.gen_p_c_profile(dynamics.p_c.Curve.length)
                    print("Percent Based Velocity Profile Generated")

                dynamics.t_c.gen_profile()
                start_bt.enable = True
                start_bt.do = False
                time_sl.x_value = 0
                dynamics.reset_pos()
                #  print(velocity_type.value)
            else:
                print("No profile to Export")
            Export_v_p.do = False

        if start_bt.do and dynamics.v_c.data_dis is not None:
            if time_start is None:
                time_start = time.time() - cur_time
            time_run = True
        else:
            time_run = False
            time_start = None

        if revers_bt.do:
            if revers_bt.init_do:
                revers_bt.init_do = False
                cur_time_s = cur_time
        else:
            if not revers_bt.init_do:
                time_start = time.time() - cur_time
                revers_bt.init_do = True

        if restart_bt.do:
            restart_bt.do = False
            time_sl.x_value = 0
            cur_time = 0
            time_start = time.time()
            start_bt.do = False

        if time_run:
            if cur_time <= dynamics.v_c.shot_time and cur_time >= 0:
                if not revers_bt.do:
                    cur_time = time.time() - time_start
                else:
                    cur_time = cur_time_s - (time.time() - time_start - cur_time_s)

            else:
                if cur_time > dynamics.v_c.shot_time:
                    cur_time = dynamics.v_c.shot_time
                elif cur_time < 0:
                    cur_time = 0
                start_bt.do = False
                idle_bt.do = False
                revers_bt.do = False

            time_sl.val_min = 0
            time_sl.val_max = dynamics.v_c.shot_time
            time_sl.update(cur_time)
        else:
            cur_time = -dynamics.v_c.shot_time * time_sl.x_value / time_sl.max_value

        for box in input_boxes:
            box.update(mouse=mouse_g)

        for drop_down in drop_downs:
            drop_down.update(mouse_g)

        for button in buttons:
            button.update(mouse_g)

        if connect_bt.do:
            if not dolly_connection:
                print("Please Wait opening Serial Connection")
                connect_dolly()
        else:
            if dolly_connection:
                print("Trying to disconect")
                disconnect_dolly()
                if not dolly_connection:
                    print("Connection closed Successfully")

        if dolly_connection:
            if send_path_bt.do:
                send_path_bt.do = False
                print("Sending path")
                data = {}
                data['name'] = path_name_txt.text
                data['duration'] = dynamics.v_c.shot_time
                data['velocity_type'] = "Percent"
                data['slam_id'] = "none"
                pos_dir = dynamics.p_c.Curve.save_control_points()
                theta_dir = dynamics.t_c.Curve.save_control_points()
                vel_dir = dynamics.v_c.Curve.save_control_points()
                data['position'] = pos_dir
                data['velocity'] = vel_dir
                data['omega'] = theta_dir
                send_path_to_dolly(data)
            if remote_start_bt.do:
                remote_start_bt.do = False
                send_timer_state("run")
            if remote_stop_bt.do:
                remote_stop_bt.do = False
                send_timer_state("stop")
            if remote_rev_bt.do:
                remote_rev_bt.do = False
                send_timer_state("reverse")
            if dump_errors_bt.do:
                dump_errors_bt.do = False
                sio.emit('errors', "")
                print("dumping errors")
            if return_home_bt.do:
                return_home_bt.do = False
                sio.emit('return_home', "")
                print("Retrurning Home")
            if update_start_bt.do:
                update_start_bt.do = False
                tracker.update_start_pos()
                sio.emit('update_pos_offset', "")
            if send_pos_pidf_bt.do:
                send_pos_pidf_bt.do = False
                pidf = {}
                pidf['pos_pidf'] = {
                    'position': {
                        'dead_zone': float(dz_in.text),
                        'p': float(p_in.text),
                        'i': float(i_in.text),
                        'd': float(d_in.text),
                        'f': float(f_in.text)
                    },
                    'rotation': {
                        'dead_zone': float(rot_dz_in.text),
                        'p': float(rot_p_in.text),
                        'i': float(rot_i_in.text),
                        'd': float(rot_d_in.text),
                        'f': float(rot_f_in.text)
                    }
                }
                dynamics.update_pidf(pidf['pos_pidf'])
                sio.emit("update_pidf", pidf)
                print(pidf)
            if send_odrive_bt.do:
                send_odrive_bt.do = False
                odrive_par["dolly"]['module']["velocity"]['current_limit'] = float(v_amp_lim.text)
                odrive_par["dolly"]['module']["velocity"]['bandwidth'] = float(v_band_lim.text)
                odrive_par["dolly"]['module']["velocity"]["k_p"] = float(v_pos_gain_in.text)
                odrive_par["dolly"]['module']["velocity"]["k_v"] = float(v_vel_gain_in.text)
                odrive_par["dolly"]['module']["velocity"]["k_vi"] = float(v_vel_i_gain_in.text)
                odrive_par["dolly"]['module']["theta"]['current_limit'] = float(t_amp_lim.text)
                odrive_par["dolly"]['module']["theta"]['bandwidth'] = float(t_band_lim.text)
                odrive_par["dolly"]['module']["theta"]["k_p"] = float(t_pos_gain_in.text)
                odrive_par["dolly"]['module']["theta"]["k_v"] = float(t_vel_gain_in.text)
                odrive_par["dolly"]['module']["theta"]["k_vi"] = float(t_vel_i_gain_in.text)
                print(odrive_par)
                sio.emit("settings", odrive_par)

        if recived_pose is not None and not recived_pose == tracker.pos:
            tracker.uupdate_pos(recived_pose, dynamics.p_c.draw_orgin, dynamics.p_c.draw_scale)

        back_ground(screen)
        dynamics.v_c.draw(screen)
        dynamics.t_c.draw(screen)
        dynamics.p_c.draw()
        dynamics.draw(screen)

        cur_time_disp = myfont.render("Simulation TIme: " + str(round(cur_time, 2)), 1, TEXT_light)
        if velocity_type.value == "Percent":
            c_l = myfont.render("%", 1, TEXT_light)
            screen.blit(c_l, velocity_w(20, 37))
        elif velocity_type.value == "Time":
            c_l = myfont.render("t", 1, TEXT_light)
            screen.blit(c_l, velocity_w(20, 37))
        screen.blit(cur_time_disp, info_w(2, 13))

        if tracker.draw_pos is not None:
            tracker.draw(dynamics.p_c.b_g)

        if dynamics.v_c.data_dis is not None:
            if cur_time != old_time or dynamics.t_c.Curve.moving:
                dynamics.update_sim_pos(cur_time)
                old_time = cur_time

        if idle_bt.do:
            if idle_bt.init_do:
                change_dolly_state(states_load.value)
                idle_bt.init_do = False
        else:
            if not idle_bt.init_do:
                change_dolly_state('disabled')
                idle_bt.init_do = True


        for box in input_boxes:
            box.draw(screen)

        for button_draw in buttons:
            button_draw.draw(screen)

        for drop_down_draw in drop_downs:
            drop_down_draw.draw(screen)

        for slider in sliders:
            slider.draw(screen)

        # Go ahead and update the screen with what we've drawn.
        dynamics.p_c.blit(screen)
        dynamics.t_c.blit(screen)

        if dynamics.p_c.Curve.moving:
            value = np.divide(np.subtract(np.subtract(mouse_g, [dynamics.p_c.window.left, dynamics.p_c.window.top]), dynamics.p_c.draw_orgin), dynamics.p_c.draw_scale)
            ind = myfont.render("X: " + str(round(value[0], 2)) + " Y: " + str(round(value[1], 2)), 1, TEXT)
            screen.blit(ind, pos_p_w(30, 5))

        if dynamics.t_c.Curve.moving:
            value = np.divide(np.subtract(np.subtract(mouse_g, [dynamics.t_c.window.left, dynamics.p_c.window.top]), dynamics.t_c.draw_orgin), dynamics.t_c.draw_scale)
            value[1] = (value[1]/math.pi)*180
            ind = myfont.render("%: " + str(round(value[0], 2)) + " Omega: " + str(round(value[1], 2)), 1, TEXT)
            screen.blit(ind, theta_p_w(25, 5))


        if dynamics.v_c.Curve.moving:
            y_scale = dynamics.v_c.Curve.window.bottom - dynamics.v_c.Curve.window.top
            y_s = constrain(((-1 * (mouse_g[1] - dynamics.v_c.Curve.window.bottom) / y_scale)), 0, 1)
            if velocity_type.value == "Time":
                x_scale = int(shot_time.text) / (dynamics.v_c.window.right - dynamics.v_c.window.left)
                x_s = constrain((mouse_g[0] - dynamics.v_c.window.left) * x_scale, 0, float(shot_time.text))
                ind = myfont.render("t: " + str(round(x_s, 2)) + " V: " + str(round(y_s, 2)), 1, TEXT)
            else:
                x_scale = 100 / (dynamics.v_c.window.right - dynamics.v_c.window.left)
                x_s = constrain((mouse_g[0] - dynamics.v_c.window.left) * x_scale, 0, 100)
                ind = myfont.render("%: " + str(round(x_s, 2)) + " V: " + str(round(y_s, 2)), 1, TEXT)
            screen.blit(ind, velocity_w(30, 10))

        pygame.display.flip()
        # Limit to 20 frames per second
        clock.tick(20)


if __name__ == "__main__":
    main()
pygame.quit()
