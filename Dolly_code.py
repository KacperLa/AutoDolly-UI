import time
from Velocity_Planning import Velocity_Profile
from Position_Planning import Position_Controller
from Theta_Controller import Theta_Profile
import os

class grid:
    """This class is designed to help arrange UI Elements"""
    def __init__(self, s_x, s_y, s_p, s_g_y, s_g_x = None):
        if s_g_x is None:
            self.s_g_x = s_g_y
        else:
            self.s_g_x = s_g_x
        self.s_x = s_x
        self.s_y = s_y
        self.s_p = s_p
        self.s_g_y = s_g_y
        self.x_w = s_x/self.s_g_x
        self.y_w = s_y/s_g_y
        self.size = (self.s_x, self.s_y)
        self.width = s_x
        self.height = s_y
        self.bottom = s_p[1]+s_y
        self.top = s_p[1]
        self.left = s_p[0]
        self.right = s_p[0]+s_x
        self.middle_w = s_p[0]+s_x/2
        self.middle_h = s_p[1]+s_y/2

    def p_calc(self, p, xy_dir):
        if xy_dir == "x":
            return self.left + (self.s_x * p)
        elif xy_dir == "y":
            return self.bottom - (self.s_y * p)

    def __call__(self, g_x, g_y, reletive=0):
        if not reletive:
            x = self.s_p[0] + (self.s_x/self.s_g_x)*g_x
            y = self.s_p[1] + (self.s_y/self.s_g_y)*g_y
        else:
            x = (self.s_x / self.s_g_x) * g_x
            y = (self.s_y / self.s_g_y) * g_y
        return [x, y]

pos_w = grid(500, 500, (250, 0), 40)
pos_p_w = grid(pos_w.x_w * 35.5, pos_w.y_w * 35.5, pos_w(3, 3), 40)

velocity_w = grid(500, 250, (750, 250), 40)
velocity_p_w = grid(velocity_w.x_w * 36, velocity_w.y_w * 31, velocity_w(2.5, 6), 40)

theta_w = grid(500, 250, (750, 0), 40)
theta_p_w = grid(theta_w.x_w * 36, theta_w.y_w * 31, theta_w(2.5, 6), 40)


orgin_time = time.time()

cur_time = 0

done = False


class Dynamics:
  def __init__(self):
    self.start_point = None
    self.path_length = None

    self.plan_mode = "Rec-path"
    self.velocity_type = "Time"

    self.v_c = Velocity_Profile(velocity_p_w)
    self.p_c = Position_Controller(pos_w)
    self.t_c = Theta_Profile(theta_p_w)

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

  def update_data(self, path_cps, theta_cps, vel_cps):
    self.v_c.Curve.load_text_profile(vel_cps)
    self.p_c.Curve.load_text_profile(path_cps)
    self.start_point = [self.p_c.Curve.start_point[0], self.p_c.Curve.start_point[1], 0]
    self.path_length = self.p_c.Curve.length

  def update_sim_pos(self, c_t):
    self.dis_new, self.vel_new, perc_new = self.v_c.interp_data_per_t(c_t)
    self.sim_rot = self.t_c.get_a_for_t(self.p_c.current_seg, self.p_c.current_t)
    self.sim_pos = self.p_c.find_xya_per_dis(self.dis_new)
    #print(self.sim_pos,self.sim_rot)

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

  def calc_pid(self):
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

  def calc_sudo_jt(self):
    v = math.sqrt(math.pow(self.x_signal, 2) + math.pow(self.y_signal, 2))
    a = math.atan2(self.x_signal, self.y_signal) + self.rel_pos[2]
    w = constrain(self.w_signal, -1, 1)
    return v, a, w

  def reset_pos(self):
    """
    Purpose: Return simulated dolly to start position
    """
    if self.start_point is not None:
      self.sim_pos = self.start_point
Controller = Dynamics()

#=================================
with open(os.path.join(os.getcwd(), "sim_paths", "bigs.json"),"r") as path_load_text:
    Controller.p_c.Curve.load_text_profile(path_load_text)
with open(os.path.join(os.getcwd(), "sim_theta", "bigs.json"),"r") as theta_load_text:
    Controller.t_c.Curve.load_text_profile(theta_load_text)

with open(os.path.join(os.getcwd(), "sim_profiles", "m_trap.json"),"r") as vel_load_text:
    Controller.v_c.Curve.load_text_profile(vel_load_text)


shot_time = Controller.p_c.Curve.shot_time
print("Shot time: ", shot_time)
# =================================
Controller.v_c.gen_p_c_profile(Controller.p_c.Curve.length)
Controller.reset_pos()

print(Controller.p_c.Curve.B)
print(Controller.p_c.Curve.t)
print(Controller.p_c.Curve.seg_k)

while not done:
  if cur_time <= shot_time:
    cur_time = time.time() - orgin_time
    print("Running", cur_time)
    Controller.update_sim_pos(cur_time)

    time.sleep(.2)
  else:
    print("Done")
    done = True
