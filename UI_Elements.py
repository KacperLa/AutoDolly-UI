import pygame
import time
import numpy as np
from theme_AD import *
import copy
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
        self.space = pygame.Rect(self.left, self.top, self.s_x, self.s_y)

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

# class timer:
#     def __init__(self):
#         self.time_start = None
#         self.new_start_time = None
#         self.time_run = False
#         self.cur_time = 0
#         self.cur_time_s = 0
#         self.old_time = 0
#
#     def run(self):
#         if self.time_start is None:
#             self.time_start = time.time() - cur_time
#         self.time_run = True
#
#     def stop(self):
#         self.time_run = False
#         self.time_start = None


class info_txt:
    """This class is responsible for displaying Info text at the at the bottom of the screen """
    def __init__(self, font, loc):
        self.loc = loc
        self.msg = None
        self.timer = 10
        self.myfont = font

    def __call__(self, msg):
        self.msg = msg
        self.cur_time = time.time()

    def draw(self, screen):
        if self.msg is not None:
            if (time.time() - self.cur_time) < self.timer:
                ze_msg = self.myfont.render("INFO: " + self.msg, 1, TEXT_light)
                screen.blit(ze_msg, self.loc)
            else:
                self.msg = None


class InputBox:
    def __init__(self, font, xy, w, h, text='10'):
        self.myfont = font
        self.active = False
        self.w = w
        x = xy[0]
        y = xy[1]
        self.COLOR_INACTIVE = (255,255,255)
        self.COLOR_ACTIVE = dark_orange
        self.rect = pygame.Rect(x, y, w, h-1)
        self.bg_rect = pygame.Rect(x, y, w, h)

        self.color = self.COLOR_INACTIVE
        self.color_text = self.COLOR_INACTIVE
        self.bg_color = UI_L1
        self.text = text
        self.txt_surface = self.myfont.render(text, True, self.color_text)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.myfont.render(self.text, True, self.color_text)

    def update(self, text = None, mouse=None):
        if not self.active and mouse is not None:
            if self.rect.collidepoint(mouse):
                self.color = ORANGE
            else:
                self.color = self.COLOR_INACTIVE

        if text is None:
            pass
        else:
            self.text = str(text)
            self.txt_surface = self.myfont.render(self.text, True, self.color_text)

        # Resize the box if the text is too long.
        width = max(self.w, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.bg_rect)
        pygame.draw.rect(screen, self.bg_color, self.rect)

        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y + (self.rect.h/2) - (self.txt_surface.get_height()/2)))


class Button:
    def __init__(self, xy, val_in, size_x, size_y, color, enable, myfont=None, label_ndo=None, label_do=None, text_color=None, color_do=None):
        self.enable = enable # Blocks button from being activated
        self.init_do = True

        self.myfont = myfont
        if text_color is not None:
            self.text_color = text_color
        else:
            self.text_color = TEXT_light

        self.label_ndo = label_ndo
        self.label_do = label_do

        self.color_disable = GRAY_1  # Color Button when Disabled

        self.color_not_doing = UI_L1  # Color of button when not active
        if color_do is not None:
            self.color_doing = color_do  # Color of Button when active
        else:
            self.color_doing = dark_orange
        self.color = self.color_not_doing  # Current color of button

        self.pos_x = int(xy[0])
        self.pos_y = int(xy[1])

        self.rounded = False
        self.shaddow_v = False

        self.size_x = size_x
        self.size_y = size_y

        if val_in:
            self.do = True
        else:
            self.do = False

        self.not_done = True
        self.shaddow = pygame.Rect(self.pos_x, self.pos_y, self.size_x, self.size_y)
        if self.label_ndo is not None:
            self.label_ndo_r = self.myfont.render(self.label_ndo, 1, self.text_color)
        else:
            self.label_ndo_r = None

        if self.label_do is not None:
            self.label_do_r = self.myfont.render(self.label_do, 1, self.text_color)
        else:
            self.label_do_r = None
        self.face = pygame.Rect(self.pos_x+1, self.pos_y, self.size_x-2, self.size_y)

    def draw(self, screen):
        if not self.enable:
            self.color = self.color_disable
            self.do = False
            label = self.label_ndo_r
        else:
            if self.do:
                self.color = self.color_doing
                if self.label_do is None:
                    label = self.label_ndo_r
                else:
                    label = self.label_do_r
            else:
                self.color = self.color_not_doing
                label = self.label_ndo_r
        if not self.rounded:
            if self.shaddow_v:
                pygame.draw.rect(screen, Gray_3, self.shaddow)
            pygame.draw.rect(screen, self.color, self.face)
        else:
            body = pygame.Rect(self.pos_x+1+(self.size_y/2), self.pos_y, self.size_x-2-(self.size_y), self.size_y)
            pygame.draw.rect(screen, self.color,body)
            c_pos_l = (int(self.pos_x+1+(self.size_y/2)), int(self.pos_y+1+(self.size_y/2)))
            c_pos_r = (int(self.pos_x+1+self.size_x-(self.size_y/2)), int(self.pos_y+1+(self.size_y/2)))
            pygame.draw.circle(screen, self.color,c_pos_l,int(self.size_y/2))
            pygame.draw.circle(screen, self.color, c_pos_r, int(self.size_y / 2))
        if label is not None:
            screen.blit(label, (self.pos_x + self.size_x/2 - label.get_width()/2, self.pos_y + self.size_y/2 - label.get_height()/2))


    def action(self):
        if self.enable:
            if self.do:
                self.do = False
            else:
                self.do = True
        else:
            self.do = False

    def update(self, mouse):
        if not self.do:
            if self.face.collidepoint(mouse):
                self.color_not_doing = ORANGE
            else:
                self.color_not_doing = UI_L1



class Slider:
    def __init__(self, xy_s, xy_e, Width, myfont=None, bubble=False, val_min=0, val_max=100, layout="x"):
        self.Width = Width
        self.layout = layout
        self.sliding = 0
        self.bubble = bubble
        self.myfont = myfont
        self.slider_width = 10
        self.head_size_x = 16
        self.head_size_y = 16
        self.xy_s = xy_s
        self.xy_e = xy_e
        self.pos_x = xy_s[0]
        self.pos_y = xy_s[1]
        self.end_x = xy_e[0]
        self.end_y = xy_e[1]
        if self.layout == "x":
            self.max_value = int(self.end_x - self.pos_x)
        if self.layout == "y":
            self.max_value = int(self.end_y - self.pos_y)

        self.min_value = 0
        self.y_value = 0
        self.x_value = 0
        self.value = 0
        self.val_min = val_min
        self.val_max = val_max
        self.end_point = [self.pos_x - self.x_value, self.pos_y - self.y_value]
        self.face = pygame.Rect(self.pos_x - self.x_value - self.head_size_x / 2, self.pos_y - self.y_value - self.head_size_y / 2,
                                self.head_size_x, self.head_size_y)
        if self.layout == "x":
            self.area = pygame.Rect(self.pos_x, self.pos_y - self.head_size_y / 2, self.max_value, self.head_size_y)
            self.bg = pygame.Rect(self.pos_x, self.pos_y - self.head_size_y / 16, self.max_value, self.head_size_y / 8)
        if self.layout == "y":
            self.area = pygame.Rect(self.pos_x - self.head_size_x / 2, self.pos_y, self.head_size_x, self.max_value)
            self.bg = pygame.Rect(self.pos_x - self.head_size_x / 16, self.pos_y, self.head_size_x/8, self.max_value)

    def update(self, value):
        if self.layout == "x":
            if value == 0:
                self.x_value = self.val_min
            else:
                self.x_value = self.max_value * value/(self.val_max - self.val_min)
            self.value = value
            self.adjust_value(self.x_value+self.pos_x)
        if self.layout == "y":
            if value == 0:
                self.y_value = self.val_min
            else:
                self.y_value = self.max_value * value/(self.val_max - self.val_min)
            self.value = value
            self.adjust_value(self.y_value+self.pos_y)

    def adjust_value(self, x_val, y_val=None):
        if self.layout == "x":
            if x_val > self.end_x:
                self.x_value = -self.max_value
            elif x_val < self.pos_x:
                self.x_value = -self.min_value
            else:
                self.x_value = self.Width - x_val - (self.Width - self.pos_x)
                self.value = abs((self.val_max - self.val_min) * self.x_value / self.max_value)
        if self.layout == "y":
            if y_val > self.end_y:
                self.y_value = -self.max_value
            elif y_val < self.pos_y:
                self.y_value = -self.min_value
            else:
                self.y_value = self.Width - y_val - (self.Width - self.pos_y)
                self.value = abs((self.val_max - self.val_min) * self.y_value / self.max_value)

    def draw(self, screen):
        if self.layout == "x":

            self.face = pygame.Rect(self.pos_x - self.x_value - self.head_size_x / 2,
                                    self.pos_y - self.head_size_y / 2.0,
                                    self.head_size_x, self.head_size_y)

            up_to_face = pygame.Rect(self.pos_x, self.pos_y - self.head_size_y / 16, -self.x_value,
                                     self.head_size_y / 8)
            pygame.draw.rect(screen, RED, self.bg)
            pygame.draw.rect(screen, UI_EH, up_to_face)
            # pygame.draw.rect(screen, UI_ES, self.face)
            c_x_pos = int(self.pos_x - self.x_value)
            c_y_pos = int(self.pos_y)
            pygame.draw.circle(screen, UI_EH, (c_x_pos, c_y_pos), 8)
            if self.sliding and self.bubble:
                pygame.draw.circle(screen, UI_ES, (c_x_pos, c_y_pos - 25), 20)
                val_text = self.myfont.render(str(round(self.value, 2)), 1, TEXT)
                screen.blit(val_text, (c_x_pos - val_text.get_width() / 2, c_y_pos - 25 - val_text.get_height() / 2))
        if self.layout == "y":
            self.face = pygame.Rect(self.pos_x - self.head_size_x / 2,
                                    self.pos_y - self.y_value - self.head_size_y / 2,
                                    self.head_size_x, self.head_size_y)

            up_to_face = pygame.Rect(self.pos_x, self.pos_y - self.head_size_y / 16, -self.x_value,
                                     self.head_size_y / 8)
            pygame.draw.rect(screen, RED, self.bg)
            pygame.draw.rect(screen, UI_EH, up_to_face)
            # pygame.draw.rect(screen, UI_ES, self.face)
            c_x_pos = int(self.pos_x)
            c_y_pos = int(self.pos_y - self.y_value)
            pygame.draw.circle(screen, UI_EH, (c_x_pos, c_y_pos), 8)
            if self.sliding and self.bubble:
                pygame.draw.circle(screen, UI_ES, (c_x_pos, c_y_pos - 25), 20)
                val_text = self.myfont.render(str(round(self.value, 2)), 1, TEXT)
                screen.blit(val_text, (c_x_pos - val_text.get_width() / 2, c_y_pos - 25 - val_text.get_height() / 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            mouse_button = event.button
            if event.button == 1:
                if self.face.collidepoint(mouse_pos):
                    self.sliding = True
            if event.button == 4:
                if self.area.collidepoint(mouse_pos):
                    self.x_value = self.x_value - 2
            if event.button == 5:
                if self.area.collidepoint(mouse_pos):
                    self.x_value = self.x_value + 2


class ctrl_point:
    def __init__(self, P, UI_orgin=None, UI_scale=None, color=None, lock=False):
        self.pos_x, self.pos_y = P
        self.point = P
        self.lock = lock

        self.UI_orgin = UI_orgin
        self.UI_scale = UI_scale
        self.moving = False

        self.draw_point = np.multiply(self.point, UI_scale)
        self.draw_point = np.add(self.draw_point, self.UI_orgin)
        self.draw_point_prev = self.draw_point
        self.color = color
        self.size_x = 10
        self.size_y = 10
        self.not_done = True
        self.face = pygame.Rect(self.point[0] - self.size_x / 2, self.point[1] - self.size_y / 2, self.size_x,
                                self.size_y)

    def draw(self, screen):
        if self.lock:
            self.color = BLUE
        self.face = pygame.Rect(self.draw_point[0] - self.size_x / 2, self.draw_point[1] - self.size_y / 2, self.size_x, self.size_y)
        pygame.draw.circle(screen, self.color, [int(self.draw_point[0]),int(self.draw_point[1])],5,0)
        self.pos_x, self.pos_y = self.point
        self.draw_point_prev = self.draw_point


    def update(self):
        _p = np.multiply(self.point, self.UI_scale)
        _p = np.add(_p, self.UI_orgin)
        self.draw_point = _p


    def click(self,mouse):

        if self.face.collidepoint(mouse) and not self.lock:
            self.moving = True

    def release(self):
        self.moving = False

    def move(self,P):
        self.draw_point = P
        _p = np.subtract(P,self.UI_orgin)
        _p = np.divide(_p, self.UI_scale)
        self.point = _p

    def move_og(self,_p):
        self.point = _p
        _P = np.multiply(_p, self.UI_scale)
        P = np.add(_P,self.UI_orgin)
        self.draw_point = P


class Drop_Down:
    def __init__(self, xy, size_x, size_y, color, enable, myfont, item_list=None):
        self.init_do = True

        self.pos_x = int(xy[0])
        self.pos_y = int(xy[1])

        self.size_x = size_x
        self.size_y = size_y

        self.triangle_down = [[self.pos_x + self.size_x*.91, self.pos_y + self.size_y*.45],[self.pos_x + self.size_x*.94, self.pos_y + self.size_y*.45],[self.pos_x + self.size_x*.925, self.pos_y + self.size_y*.6]]
        self.triangle_up = [[self.pos_x + self.size_x*.91, self.pos_y + self.size_y*.6],[self.pos_x + self.size_x*.94, self.pos_y + self.size_y*.6],[self.pos_x + self.size_x*.925, self.pos_y + self.size_y*.45]]

        self.myfont = myfont
        self.item_list = ["No Items to display", ]
        self.item_buttons = None
        self.item_colors = None
        self.item_list_r = None
        self.padding = None
        self.open_face = None
        self.update_list(item_list)
        self.disp_item = self.item_list_r[0]
        self.value = self.item_list[0]
        self.COLOR_INACTIVE = (255, 255, 255)
        self.COLOR_ACTIVE = dark_orange

        self.color_closed = color  # Color of button when not active
        self.color_open = ORANGE  # Color of Button when active
        self.color = self.COLOR_INACTIVE  # Current color of button

        self.active = False

        self.not_done = True
        self.shaddow_closed = pygame.Rect(self.pos_x, self.pos_y, self.size_x, self.size_y)
        self.rect = pygame.Rect(self.pos_x, self.pos_y, self.size_x, self.size_y-1)


    def update_list(self, item_list):
        if len(item_list) == 0:
            item_list = ["No item",]
        self.item_list = item_list
        self.item_list_r = []
        self.item_buttons = []
        self.item_colors = []
        for index, item in enumerate(item_list):
            self.item_list_r.append(self.myfont.render(item, 1, TEXT_light))
            self.item_buttons.append(pygame.Rect(self.pos_x, self.pos_y+((index+1)*self.size_y), self.size_x, self.size_y))
            self.item_colors.append(UI_L1)
        _text_size_y = self.item_list_r[0].get_height()
        self.padding = (self.size_y - _text_size_y)/2
        self.open_face = pygame.Rect(self.pos_x, self.pos_y + self.size_y, self.size_x, (_text_size_y*(len(item_list))+self.padding*(len(item_list)+2)+1))

    def draw(self, screen):
        if self.active:

            pygame.draw.rect(screen, self.color, self.shaddow_closed)
            pygame.draw.rect(screen, UI_L1, self.rect)
            pygame.draw.rect(screen, UI_L1, self.open_face)
            pygame.draw.polygon(screen, self.color, self.triangle_up)

            for button, color in zip(self.item_buttons, self.item_colors):
                pygame.draw.rect(screen, color, button)

            screen.blit(self.disp_item, (self.pos_x + 5, self.pos_y + self.size_y / 2 - self.disp_item.get_height() / 2))

            for index, item in enumerate(self.item_list_r):
                screen.blit(item, (self.pos_x + 5, self.pos_y + (index+1)*self.size_y + self.size_y / 2 - item.get_height() / 2))

        else:

            pygame.draw.rect(screen, self.color, self.shaddow_closed)
            pygame.draw.rect(screen, UI_L1, self.rect)
            screen.blit(self.disp_item, (self.pos_x + 5, self.pos_y + self.size_y / 2 - self.disp_item.get_height() / 2))
            pygame.draw.polygon(screen, self.color, self.triangle_down)

    def select_item(self, mouse):
        for index, button in enumerate(self.item_buttons):
                if button.collidepoint(mouse):
                    self.disp_item = self.item_list_r[index]
                    self.value = self.item_list[index]
                    self.action()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.active:
                for index, button in enumerate(self.item_buttons):
                    if button.collidepoint(event.pos):
                        self.disp_item = self.item_list_r[index]
                        self.value = self.item_list[index]
            # If the user clicked on the drop_down_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE


    def update(self, mouse):
        if self.active:
            for index, button in enumerate(self.item_buttons):
                if button.collidepoint(mouse):
                    self.item_colors[index] = ORANGE
                else:
                    self.item_colors[index] = UI_L1
        else:
            if self.rect.collidepoint(mouse):
                self.color = ORANGE
            else:
                self.color = self.COLOR_INACTIVE


