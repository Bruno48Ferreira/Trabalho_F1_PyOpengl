import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

CAR_LENGTH = 5.5
CAR_WIDTH = 2.0
CAR_HEIGHT = 1.0
WHEEL_RADIUS = 0.40
WHEEL_WIDTH = 0.45
WHEELBASE = 3.6
PLANK_THICK = 0.02

FRONT_AXLE_Z = -WHEELBASE / 2.0
REAR_AXLE_Z = WHEELBASE / 2.0
FRONT_WING_Z = FRONT_AXLE_Z - 1.0
REAR_WING_Z = REAR_AXLE_Z + 0.7

BLACK_MAIN = (0.12, 0.12, 0.14)
BLACK_PLANK = (0.06, 0.06, 0.07)
DARK_GREY = (0.25, 0.25, 0.28)
PETRONAS_TEAL = (0.0, 0.83, 0.78)
PETRONAS_LIGHT = (0.55, 1.0, 1.0)
SILVER_STRIPE = (0.84, 0.84, 0.88)
INEOS_RED = (0.86, 0.18, 0.18)
WHITE_SPONSOR = (0.97, 0.97, 0.97)
P_ZERO_YELLOW = (1.0, 0.9, 0.1)
HUB_GREY = (0.55, 0.55, 0.58)

CUBE_VERTICES = (
    (-0.5, -0.5, -0.5),
    (0.5, -0.5, -0.5),
    (0.5, 0.5, -0.5),
    (-0.5, 0.5, -0.5),
    (-0.5, -0.5, 0.5),
    (0.5, -0.5, 0.5),
    (0.5, 0.5, 0.5),
    (-0.5, 0.5, 0.5),
)

CUBE_FACES = (
    (0, 1, 2, 3),
    (3, 2, 6, 7),
    (1, 5, 6, 2),
    (4, 5, 1, 0),
    (4, 0, 3, 7),
    (5, 4, 7, 6),
)

def draw_box(w, h, d):
    glPushMatrix()
    glScalef(w, h, d)
    glBegin(GL_QUADS)
    for face in CUBE_FACES:
        for v in face:
            glVertex3fv(CUBE_VERTICES[v])
    glEnd()
    glPopMatrix()

def draw_cylinder(radius=0.35, length=0.25, segments=32):
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        a = 2.0 * math.pi * i / segments
        y = math.cos(a) * radius
        z = math.sin(a) * radius
        glVertex3f(-length / 2.0, y, z)
        glVertex3f(length / 2.0, y, z)
    glEnd()
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(-length / 2.0, 0.0, 0.0)
    for i in range(segments + 1):
        a = 2.0 * math.pi * i / segments
        y = math.cos(a) * radius
        z = math.sin(a) * radius
        glVertex3f(-length / 2.0, y, z)
    glEnd()
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(length / 2.0, 0.0, 0.0)
    for i in range(segments + 1):
        a = 2.0 * math.pi * i / segments
        y = math.cos(a) * radius
        z = math.sin(a) * radius
        glVertex3f(length / 2.0, y, z)
    glEnd()

def draw_ring(radius_inner, radius_outer, x, color, segments=64):
    glColor3f(*color)
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(segments + 1):
        a = 2.0 * math.pi * i / segments
        cy = math.cos(a)
        cz = math.sin(a)
        glVertex3f(x, cy * radius_outer, cz * radius_outer)
        glVertex3f(x, cy * radius_inner, cz * radius_inner)
    glEnd()

def draw_disc(radius, x, color, segments=64):
    glColor3f(*color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(x, 0.0, 0.0)
    for i in range(segments + 1):
        a = 2.0 * math.pi * i / segments
        y = math.cos(a) * radius
        z = math.sin(a) * radius
        glVertex3f(x, y, z)
    glEnd()

def draw_wheel(radius, length, wheel_angle):
    glPushMatrix()
    glRotatef(wheel_angle, 1, 0, 0)
    glColor3f(0.02, 0.02, 0.02)
    draw_cylinder(radius, length, 40)
    face_x = length / 2.0 + 0.002
    draw_ring(radius * 0.96, radius * 1.02, face_x, P_ZERO_YELLOW)
    draw_ring(radius * 0.70, radius * 0.90, face_x, PETRONAS_TEAL)
    draw_disc(radius * 0.55, face_x + 0.001, HUB_GREY)
    glPopMatrix()

def draw_front_wing():
    base_y = WHEEL_RADIUS - 0.20
    base_z = FRONT_WING_Z
    main_span = CAR_WIDTH * 1.30
    main_depth = 0.85
    flap_thick = 0.025
    glPushMatrix()
    glTranslatef(0.0, base_y, base_z)
    glColor3f(*BLACK_MAIN)
    draw_box(main_span, 0.05, main_depth)
    glPopMatrix()
    half_main = main_span / 2.0
    margin = 0.03
    for side in (-1, 1):
        side_sign = float(side)
        for i in range(4):
            t = i / 3.0
            span = (main_span * 0.32) * (1.0 - 0.10 * i)
            depth = 0.45
            y = base_y + 0.03 + 0.03 * i
            z = base_z + 0.05 + 0.06 * i
            center_x = side_sign * (half_main - margin - span / 2.0)
            attack_angle = -8.0 - 6.0 * t
            sweep_angle = 4.0 * side_sign * t
            glPushMatrix()
            glTranslatef(center_x, y, z)
            glRotatef(sweep_angle, 0, 0, 1)
            glRotatef(attack_angle, 1, 0, 0)
            glColor3f(*PETRONAS_TEAL)
            draw_box(span, flap_thick, depth)
            glPopMatrix()
    for i in range(2):
        z_off = base_z + 0.10 + i * 0.16
        glPushMatrix()
        glTranslatef(0.0, base_y + 0.02 + i * 0.02, z_off)
        glRotatef(-10.0, 1, 0, 0)
        glColor3f(*PETRONAS_TEAL)
        draw_box(CAR_WIDTH * 0.45, flap_thick, 0.35)
        glPopMatrix()
    endplate_height = 0.22
    endplate_depth = 0.65
    endplate_thick = 0.06
    for side in (-1, 1):
        side_sign = float(side)
        x = side_sign * (main_span / 2.0 - endplate_thick / 2.0)
        y = base_y + endplate_height / 2.0
        z = base_z + 0.10
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(6.0 * side_sign, 0, 1, 0)
        glColor3f(*BLACK_MAIN)
        draw_box(endplate_thick, endplate_height, endplate_depth)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(x, y + endplate_height / 2.0 + 0.01, z + endplate_depth * 0.10)
        glRotatef(6.0 * side_sign, 0, 1, 0)
        glColor3f(*PETRONAS_LIGHT)
        draw_box(endplate_thick * 1.02, 0.03, endplate_depth * 0.50)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, base_y + 0.03, base_z + 0.20)
    glColor3f(*WHITE_SPONSOR)
    draw_box(CAR_WIDTH * 0.20, 0.015, 0.20)
    glPopMatrix()

def draw_floor():
    base_y = WHEEL_RADIUS - 0.20
    mid_len = 2.4
    mid_width = CAR_WIDTH * 0.95
    mid_z = (FRONT_AXLE_Z + REAR_AXLE_Z) / 2.0
    glPushMatrix()
    glTranslatef(0.0, base_y, mid_z)
    glColor3f(*BLACK_PLANK)
    draw_box(mid_width, PLANK_THICK, mid_len)
    glPopMatrix()
    rear_len = 1.3
    rear_width = CAR_WIDTH * 0.80
    rear_center_end = REAR_AXLE_Z + 0.25
    rear_z = rear_center_end - rear_len / 2.0
    glPushMatrix()
    glTranslatef(0.0, base_y, rear_z)
    glColor3f(*BLACK_PLANK)
    draw_box(rear_width, PLANK_THICK, rear_len)
    glPopMatrix()
    edge_len = mid_len * 0.90
    edge_width = 0.05
    edge_z = mid_z
    for side in (-1, 1):
        side_sign = float(side)
        x = side_sign * (mid_width / 2.0 - edge_width / 2.0)
        glPushMatrix()
        glTranslatef(x, base_y + 0.001, edge_z)
        glColor3f(*PETRONAS_TEAL)
        draw_box(edge_width, 0.01, edge_len)
        glPopMatrix()
    diff_len = 0.6
    diff_width = rear_width * 0.95
    diff_z = REAR_AXLE_Z + 0.35
    glPushMatrix()
    glTranslatef(0.0, base_y + 0.05, diff_z)
    glRotatef(-12.0, 1, 0, 0)
    glColor3f(*BLACK_PLANK)
    draw_box(diff_width, PLANK_THICK, diff_len)
    glPopMatrix()
    front_len = 1.0
    front_width = CAR_WIDTH * 0.55
    front_z = FRONT_AXLE_Z - 0.10
    glPushMatrix()
    glTranslatef(0.0, base_y + 0.005, front_z)
    glColor3f(*BLACK_PLANK)
    draw_box(front_width, PLANK_THICK, front_len)
    glPopMatrix()

def draw_wishbone(p_inner, p_outer, y, thickness=0.03):
    x1, z1 = p_inner
    x2, z2 = p_outer
    dx = x2 - x1
    dz = z2 - z1
    length = math.sqrt(dx * dx + dz * dz)
    if length <= 0:
        return
    angle_y = math.degrees(math.atan2(dx, dz))
    cx = (x1 + x2) / 2.0
    cz = (z1 + z2) / 2.0
    glPushMatrix()
    glTranslatef(cx, y, cz)
    glRotatef(angle_y, 0, 1, 0)
    glColor3f(0.03, 0.03, 0.03)
    draw_box(length, thickness, thickness)
    glPopMatrix()

def draw_car(wheel_angle, drs_open):
    draw_floor()
    chassis_height = 0.32
    front_chassis_len = 2.1
    rear_chassis_len = 2.0
    front_chassis_width = CAR_WIDTH * 0.55
    rear_chassis_width = CAR_WIDTH * 0.70
    glPushMatrix()
    glTranslatef(0.0, WHEEL_RADIUS - 0.18 + PLANK_THICK + chassis_height / 2.0, FRONT_AXLE_Z + 0.2)
    glColor3f(*BLACK_MAIN)
    draw_box(front_chassis_width, chassis_height, front_chassis_len)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, WHEEL_RADIUS - 0.18 + PLANK_THICK + chassis_height / 2.0, 0.55)
    glColor3f(*BLACK_MAIN)
    draw_box(rear_chassis_width, chassis_height, rear_chassis_len)
    glPopMatrix()
    nose_base_y = WHEEL_RADIUS - 0.18 + PLANK_THICK
    glPushMatrix()
    glTranslatef(0.0, nose_base_y - 0.02, FRONT_WING_Z + 0.55)
    glColor3f(*BLACK_MAIN)
    draw_box(CAR_WIDTH * 0.52, 0.04, 0.80)
    glPopMatrix()
    mid_nose_len = 1.20
    mid_nose_width = CAR_WIDTH * 0.30
    mid_nose_h = 0.22
    glPushMatrix()
    glTranslatef(0.0, nose_base_y + mid_nose_h / 2.0 + 0.04, FRONT_AXLE_Z - 0.10)
    glColor3f(*BLACK_MAIN)
    draw_box(mid_nose_width, mid_nose_h, mid_nose_len)
    glPopMatrix()
    tip_nose_len = 0.95
    tip_nose_width = CAR_WIDTH * 0.22
    tip_nose_h = 0.20
    glPushMatrix()
    glTranslatef(0.0, nose_base_y + tip_nose_h / 2.0 - 0.02, FRONT_WING_Z + 0.75)
    glColor3f(*BLACK_MAIN)
    draw_box(tip_nose_width, tip_nose_h, tip_nose_len)
    glPopMatrix()
    bridge_len = 0.60
    glPushMatrix()
    glTranslatef(0.0, nose_base_y + mid_nose_h * 0.65, FRONT_AXLE_Z - 0.35)
    glColor3f(*BLACK_MAIN)
    draw_box(mid_nose_width * 0.95, 0.14, bridge_len)
    glPopMatrix()
    for side in (-1, 1):
        side_sign = float(side)
        pillar_x = side_sign * (tip_nose_width / 2.0 - 0.03)
        glPushMatrix()
        glTranslatef(pillar_x, nose_base_y + 0.05, FRONT_WING_Z + 0.68)
        glColor3f(*BLACK_MAIN)
        draw_box(0.06, 0.16, 0.35)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, nose_base_y - 0.03, FRONT_WING_Z + 0.55)
    glColor3f(*PETRONAS_TEAL)
    draw_box(CAR_WIDTH * 0.40, 0.02, 0.70)
    glPopMatrix()
    cockpit_base_y = WHEEL_RADIUS - 0.18 + PLANK_THICK + chassis_height
    cockpit_len = 1.35
    cockpit_width = CAR_WIDTH * 0.50
    cockpit_h = 0.26
    glPushMatrix()
    glTranslatef(0.0, cockpit_base_y + cockpit_h / 2.0, -0.45)
    glColor3f(*BLACK_MAIN)
    draw_box(cockpit_width, cockpit_h, cockpit_len)
    glPopMatrix()
    for side in (-1, 1):
        side_sign = float(side)
        glPushMatrix()
        glTranslatef(side_sign * (cockpit_width / 2.0 - 0.025), cockpit_base_y + cockpit_h / 2.0 + 0.02, -0.50)
        glColor3f(*SILVER_STRIPE)
        draw_box(0.03, 0.06, 0.80)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, cockpit_base_y + cockpit_h + 0.005, -0.50)
    glColor3f(*DARK_GREY)
    draw_box(cockpit_width * 1.02, 0.02, cockpit_len * 1.02)
    glPopMatrix()
    open_len = 0.95
    open_width = cockpit_width * 0.58
    open_h = 0.20
    glPushMatrix()
    glTranslatef(0.0, cockpit_base_y + open_h / 2.0 + 0.04, -0.60)
    glColor3f(0.02, 0.02, 0.02)
    draw_box(open_width, open_h, open_len)
    glPopMatrix()
    for side in (-1, 1):
        side_sign = float(side)
        glPushMatrix()
        glTranslatef(side_sign * (open_width / 2.0 + 0.03), cockpit_base_y + 0.16, -0.60)
        glColor3f(*BLACK_MAIN)
        draw_box(0.06, 0.18, 0.70)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, cockpit_base_y + 0.22, -0.90)
    glColor3f(*BLACK_MAIN)
    draw_box(open_width * 0.85, 0.22, 0.28)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, cockpit_base_y + 0.05, -0.70)
    glColor3f(0.04, 0.04, 0.05)
    draw_box(open_width * 0.75, 0.10, 0.55)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, cockpit_base_y + 0.18, -0.38)
    glColor3f(*DARK_GREY)
    draw_box(0.26, 0.03, 0.15)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, cockpit_base_y + 0.185, -0.38)
    glColor3f(*PETRONAS_TEAL)
    draw_box(0.16, 0.01, 0.06)
    glPopMatrix()
    halo_y = cockpit_base_y + cockpit_h + 0.06
    glColor3f(*BLACK_MAIN)
    glPushMatrix()
    glTranslatef(0.0, halo_y - 0.18, -0.70)
    draw_box(0.08, 0.30, 0.08)
    glPopMatrix()
    for side in (-1, 1):
        side_sign = float(side)
        glPushMatrix()
        glTranslatef((cockpit_width / 2.0 - 0.06) * side_sign, halo_y - 0.10, -0.28)
        draw_box(0.08, 0.40, 0.08)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, halo_y + 0.04, -0.40)
    draw_box(cockpit_width + 0.30, 0.08, 0.10)
    glPopMatrix()
    airbox_width = 0.50
    airbox_height = 0.35
    airbox_len = 0.55
    glPushMatrix()
    glTranslatef(0.0, halo_y + 0.18, -0.1)
    glColor3f(*BLACK_MAIN)
    draw_box(airbox_width, airbox_height * 0.6, airbox_len)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, halo_y + 0.18 + airbox_height * 0.35, -0.1)
    glColor3f(*INEOS_RED)
    draw_box(airbox_width * 0.85, airbox_height * 0.35, airbox_len * 0.9)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, halo_y + 0.05, 1.1)
    glColor3f(*BLACK_MAIN)
    draw_box(0.10, 0.70, 2.0)
    glPopMatrix()
    sidepod_len = 1.8
    sidepod_h = 0.45
    sidepod_width = 0.70
    for side in (-1, 1):
        side_sign = float(side)
        glPushMatrix()
        glTranslatef(side_sign * (CAR_WIDTH / 2.0 - sidepod_width / 2.0), WHEEL_RADIUS - 0.18 + PLANK_THICK + sidepod_h / 2.0, 0.3)
        glColor3f(*BLACK_MAIN)
        draw_box(sidepod_width, sidepod_h, sidepod_len)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(side_sign * (CAR_WIDTH / 2.0 - sidepod_width / 2.0), WHEEL_RADIUS - 0.18 + PLANK_THICK + sidepod_h / 2.0 - 0.18, -0.1)
        glColor3f(*BLACK_MAIN)
        draw_box(sidepod_width * 0.9, sidepod_h * 0.6, sidepod_len * 0.8)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(side_sign * (CAR_WIDTH / 2.0 - sidepod_width + 0.05), WHEEL_RADIUS - 0.18 + PLANK_THICK + 0.15, 0.25)
        glColor3f(*PETRONAS_TEAL)
        draw_box(0.05, 0.18, 1.4)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(side_sign * (CAR_WIDTH / 2.0 - sidepod_width + 0.055), WHEEL_RADIUS - 0.18 + PLANK_THICK + 0.27, 0.25)
        glColor3f(*WHITE_SPONSOR)
        draw_box(0.02, 0.06, 1.10)
        glPopMatrix()
    draw_front_wing()
    rear_wing_width = CAR_WIDTH * 0.95
    endplate_thick = 0.06
    endplate_height = 1.05
    endplate_depth = 0.22
    for side in (-1, 1):
        side_sign = float(side)
        x = side_sign * (rear_wing_width / 2.0 - endplate_thick / 2.0)
        y = WHEEL_RADIUS + 0.15 + endplate_height / 2.0
        z = REAR_WING_Z
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(*BLACK_MAIN)
        draw_box(endplate_thick, endplate_height, endplate_depth)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(x, WHEEL_RADIUS + 0.15 + endplate_height - 0.06, z + 0.01)
        glColor3f(*PETRONAS_TEAL)
        draw_box(endplate_thick * 1.05, 0.10, endplate_depth * 0.60)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(x, WHEEL_RADIUS + 0.15 + endplate_height * 0.35, z + endplate_depth * 0.20)
        glColor3f(*WHITE_SPONSOR)
        draw_box(endplate_thick * 1.01, 0.20, 0.04)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, WHEEL_RADIUS + 0.65, REAR_AXLE_Z + 0.25)
    glColor3f(*BLACK_MAIN)
    draw_box(0.12, 1.0, 0.12)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, WHEEL_RADIUS + 0.55, REAR_AXLE_Z + 0.10)
    glColor3f(*BLACK_MAIN)
    draw_box(0.45, 0.35, 0.60)
    glPopMatrix()
    beam_y = WHEEL_RADIUS + 0.40
    glPushMatrix()
    glTranslatef(0.0, beam_y, REAR_WING_Z - 0.05)
    glColor3f(*BLACK_MAIN)
    draw_box(rear_wing_width * 0.90, 0.10, 0.15)
    glPopMatrix()
    main_y = WHEEL_RADIUS + 0.80
    main_depth = 0.15
    main_thick = 0.18
    glPushMatrix()
    glTranslatef(0.0, main_y, REAR_WING_Z)
    glColor3f(*BLACK_MAIN)
    draw_box(rear_wing_width, main_thick, main_depth)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, main_y + 0.01, REAR_WING_Z + 0.02)
    glColor3f(*WHITE_SPONSOR)
    draw_box(rear_wing_width * 0.55, 0.02, 0.18)
    glPopMatrix()
    flap_depth = 0.25
    flap_thick = 0.03
    drs_angle = -38.0 if drs_open else 0.0
    glPushMatrix()
    glTranslatef(0.0, main_y + 0.30, REAR_WING_Z)
    glTranslatef(0.0, 0.0, flap_depth / 2.0)
    glRotatef(drs_angle, 1, 0, 0)
    glTranslatef(0.0, 0.0, -flap_depth / 2.0)
    glColor3f(*BLACK_MAIN)
    draw_box(rear_wing_width * 0.98, flap_thick, flap_depth)
    glPopMatrix()
    glColor3f(0.06, 0.06, 0.07)
    wheel_offset_x = CAR_WIDTH / 2.0 - 0.10
    positions = [
        (wheel_offset_x, WHEEL_RADIUS, FRONT_AXLE_Z),
        (-wheel_offset_x, WHEEL_RADIUS, FRONT_AXLE_Z),
        (wheel_offset_x, WHEEL_RADIUS, REAR_AXLE_Z),
        (-wheel_offset_x, WHEEL_RADIUS, REAR_AXLE_Z),
    ]
    for (x, y, z) in positions:
        glPushMatrix()
        glTranslatef(x, y, z)
        draw_wheel(WHEEL_RADIUS, WHEEL_WIDTH, wheel_angle)
        glPopMatrix()
    susp_y_upper = WHEEL_RADIUS + 0.05
    susp_y_lower = WHEEL_RADIUS - 0.05
    for side in (-1, 1):
        side_sign = float(side)
        front_inner_upper = (side_sign * (CAR_WIDTH * 0.30), FRONT_AXLE_Z + 0.25)
        front_inner_lower = (side_sign * (CAR_WIDTH * 0.32), FRONT_AXLE_Z + 0.10)
        front_outer = (side_sign * (wheel_offset_x - 0.05), FRONT_AXLE_Z)
        draw_wishbone(front_inner_upper, front_outer, susp_y_upper, 0.025)
        draw_wishbone(front_inner_lower, front_outer, susp_y_lower, 0.025)
        rear_inner_upper = (side_sign * (CAR_WIDTH * 0.28), REAR_AXLE_Z - 0.20)
        rear_inner_lower = (side_sign * (CAR_WIDTH * 0.30), REAR_AXLE_Z - 0.05)
        rear_outer = (side_sign * (wheel_offset_x - 0.05), REAR_AXLE_Z)
        draw_wishbone(rear_inner_upper, rear_outer, susp_y_upper, 0.025)
        draw_wishbone(rear_inner_lower, rear_outer, susp_y_lower, 0.025)

def draw_track():
    track_width = 10.0
    half_width = track_width / 2.0
    z_min = -2000.0
    z_max = 2000.0
    y_grass = -0.1
    y_asphalt = 0.0
    y_edge = 0.05
    y_center = 0.06
    glColor3f(0.0, 0.45, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-30.0, y_grass, z_min)
    glVertex3f(30.0, y_grass, z_min)
    glVertex3f(30.0, y_grass, z_max)
    glVertex3f(-30.0, y_grass, z_max)
    glEnd()
    glColor3f(0.22, 0.22, 0.24)
    glBegin(GL_QUADS)
    glVertex3f(-half_width, y_asphalt, z_min)
    glVertex3f(half_width, y_asphalt, z_min)
    glVertex3f(half_width, y_asphalt, z_max)
    glVertex3f(-half_width, y_asphalt, z_max)
    glEnd()
    glColor3f(0.9, 0.9, 0.9)
    edge_width = 0.2
    glBegin(GL_QUADS)
    glVertex3f(half_width, y_edge, z_min)
    glVertex3f(half_width - edge_width, y_edge, z_min)
    glVertex3f(half_width - edge_width, y_edge, z_max)
    glVertex3f(half_width, y_edge, z_max)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(-half_width, y_edge, z_min)
    glVertex3f(-half_width + edge_width, y_edge, z_min)
    glVertex3f(-half_width + edge_width, y_edge, z_max)
    glVertex3f(-half_width, y_edge, z_max)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    line_width = 0.25
    segment_length = 4.0
    gap = 4.0
    z = z_min
    while z < z_max:
        glBegin(GL_QUADS)
        glVertex3f(-line_width / 2.0, y_center, z)
        glVertex3f(line_width / 2.0, y_center, z)
        glVertex3f(line_width / 2.0, y_center, z + segment_length)
        glVertex3f(-line_width / 2.0, y_center, z + segment_length)
        glEnd()
        z += segment_length + gap

def create_text_texture(text, font, color=(255, 255, 255)):
    surface = font.render(text, True, color)
    text_data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id, width, height

def draw_textured_quad_2d(tex_id, x, y, w, h, window_width, window_height):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex2f(x, y)
    glTexCoord2f(1.0, 0.0); glVertex2f(x + w, y)
    glTexCoord2f(1.0, 1.0); glVertex2f(x + w, y + h)
    glTexCoord2f(0.0, 1.0); glVertex2f(x, y + h)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def init_opengl(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width / float(height), 1.0, 5000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.35, 0.55, 0.90, 1.0)

def main():
    pygame.init()
    pygame.display.set_caption("CG - F1 Mercedes W12 (PyOpenGL + pygame)")
    pygame.font.init()
    window_size = [1280, 720]
    screen = pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL | RESIZABLE)
    init_opengl(window_size[0], window_size[1])
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18, bold=True)
    help_lines = [
        "ESPACO: iniciar/pausar animacao    D: alternar DRS",
        "Setas CIMA/BAIXO: acelerar/frear    Scroll do mouse: zoom",
        "ESC: sair    Mouse: orbita camera"
    ]
    help_textures = []
    for line in help_lines:
        tex_id, w, h = create_text_texture(line, font)
        help_textures.append((tex_id, w, h))
    running = True
    animation_running = False
    animation_finished = False
    car_speed = 0.0
    max_speed = 50.0
    accel = 25.0
    brake_accel = 40.0
    car_z = 0.0
    travel_distance = 0.0
    max_distance = 1200.0
    wheel_angle = 0.0
    drs_open = False
    steer_angle = 0.0
    camera_yaw = 0.0
    camera_pitch = -20.0
    camera_distance = 10.0
    mouse_sensitivity = 0.15
    zoom_step = 1.0
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    pygame.mouse.get_rel()
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == VIDEORESIZE:
                window_size[0], window_size[1] = event.w, event.h
                screen = pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL | RESIZABLE)
                init_opengl(window_size[0], window_size[1])
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE and not animation_finished:
                    animation_running = not animation_running
                    if not animation_running:
                        car_speed = 0.0
                elif event.key == K_d:
                    drs_open = not drs_open
            elif event.type == MOUSEWHEEL:
                camera_distance -= event.y * zoom_step
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            steer_angle += 40.0 * dt
        if keys[K_RIGHT]:
            steer_angle -= 40.0 * dt
        steer_angle = max(-20.0, min(20.0, steer_angle))
        if keys[K_UP] and animation_running and not animation_finished:
            car_speed += accel * dt
        if keys[K_DOWN] and animation_running and not animation_finished:
            car_speed -= brake_accel * dt
        if animation_running and not animation_finished:
            if travel_distance < max_distance * 0.5:
                car_speed += accel * dt
            elif travel_distance < max_distance * 0.8:
                if car_speed < max_speed:
                    car_speed += accel * 0.3 * dt
                else:
                    car_speed -= brake_accel * 0.1 * dt
            else:
                car_speed -= brake_accel * dt
                if car_speed < 0.0:
                    car_speed = 0.0
                    animation_finished = True
        car_speed = max(0.0, min(car_speed, max_speed))
        distance_step = car_speed * dt
        car_z -= distance_step
        travel_distance += distance_step
        wheel_circumference = 2.0 * math.pi * WHEEL_RADIUS
        if wheel_circumference > 0:
            wheel_angle += (distance_step / wheel_circumference) * 360.0
        mx, my = pygame.mouse.get_rel()
        camera_yaw -= mx * mouse_sensitivity
        camera_pitch -= my * mouse_sensitivity
        camera_pitch = max(-80.0, min(80.0, camera_pitch))
        camera_distance = max(5.0, min(30.0, camera_distance))
        yaw_rad = math.radians(camera_yaw)
        pitch_rad = math.radians(camera_pitch)
        target_x = 0.0
        target_y = 0.8
        target_z = car_z
        cam_x = target_x + camera_distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        cam_y = target_y + camera_distance * math.sin(pitch_rad)
        cam_z = target_z + camera_distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        cam_y = max(1.0, cam_y)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(cam_x, cam_y, cam_z, target_x, target_y, target_z, 0.0, 1.0, 0.0)
        draw_track()
        glPushMatrix()
        glTranslatef(0.0, 0.0, car_z)
        glRotatef(steer_angle, 0, 1, 0)
        draw_car(wheel_angle, drs_open)
        glPopMatrix()
        for i, (tex_id, tw, th) in enumerate(help_textures):
            margin = 10
            x = margin
            y = window_size[1] - (th + margin) - i * (th + 4)
            draw_textured_quad_2d(tex_id, x, y, tw, th, window_size[0], window_size[1])
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
