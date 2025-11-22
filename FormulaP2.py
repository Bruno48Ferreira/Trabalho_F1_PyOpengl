import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# ----- Dimensões aproximadas em escala real (1 unidade = 1 metro) -----
CAR_LENGTH   = 5.5
CAR_WIDTH    = 2.0
CAR_HEIGHT   = 1.0
WHEEL_RADIUS = 0.40   # raio maior
WHEEL_WIDTH  = 0.45   # roda mais larga
WHEELBASE    = 3.6
PLANK_THICK  = 0.02

FRONT_AXLE_Z = -WHEELBASE / 2.0   # ~ -1.8 m
REAR_AXLE_Z  =  WHEELBASE / 2.0   # ~ +1.8 m

FRONT_WING_Z = FRONT_AXLE_Z - 1.0 # ~ -2.8 m (asa dianteira)
REAR_WING_Z  = REAR_AXLE_Z  + 0.7 # ~  2.5 m (asa traseira)

# ----- Cores aproximadas da Mercedes W12 -----
BLACK_MAIN      = (0.02, 0.02, 0.03)   # preto principal
BLACK_PLANK     = (0.03, 0.03, 0.03)   # fundo do carro
DARK_GREY       = (0.08, 0.08, 0.09)
PETRONAS_TEAL   = (0.0, 0.78, 0.75)    # teal PETRONAS
PETRONAS_LIGHT  = (0.3, 0.95, 0.95)    # teal mais claro (detalhes)
SILVER_STRIPE   = (0.80, 0.80, 0.84)   # faixas AMG
INEOS_RED       = (0.65, 0.10, 0.10)   # topo da tomada de ar
WHITE_SPONSOR   = (0.95, 0.95, 0.95)
PLANK_BROWN    = (0.18, 0.11, 0.04)   # cor da madeira do plank


# ----------------- PRIMITIVAS BÁSICAS -----------------

CUBE_VERTICES = (
    (-0.5, -0.5, -0.5),
    ( 0.5, -0.5, -0.5),
    ( 0.5,  0.5, -0.5),
    (-0.5,  0.5, -0.5),
    (-0.5, -0.5,  0.5),
    ( 0.5, -0.5,  0.5),
    ( 0.5,  0.5,  0.5),
    (-0.5,  0.5,  0.5),
)

CUBE_FACES = (
    (0, 1, 2, 3),
    (3, 2, 6, 7),
    (1, 5, 6, 2),
    (4, 5, 1, 0),
    (4, 0, 3, 7),
    (5, 4, 7, 6),
)


def draw_box(width, height, depth):
    """Desenha uma caixa com centro na origem."""
    glPushMatrix()
    glScalef(width, height, depth)
    glBegin(GL_QUADS)
    for face in CUBE_FACES:
        for v in face:
            glVertex3fv(CUBE_VERTICES[v])
    glEnd()
    glPopMatrix()


def draw_cylinder(radius=0.35, length=0.25, segments=24):
    """
    Cilindro com eixo ao longo do eixo X.
    Usado para as rodas.
    """
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        y = math.cos(angle) * radius
        z = math.sin(angle) * radius
        glVertex3f(-length / 2.0, y, z)
        glVertex3f( length / 2.0, y, z)
    glEnd()

    # Tampa esquerda (-X)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(-length / 2.0, 0.0, 0.0)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        y = math.cos(angle) * radius
        z = math.sin(angle) * radius
        glVertex3fv((-length / 2.0, y, z))
    glEnd()

    # Tampa direita (+X)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(length / 2.0, 0.0, 0.0)
    for i in range(segments + 1):
        angle = 2.0 * math.pi * i / segments
        y = math.cos(angle) * radius
        z = math.sin(angle) * radius
        glVertex3fv((length / 2.0, y, z))
    glEnd()

def draw_front_wing():
    """
    Asa dianteira mais detalhada, simulando curvas com vários flaps
    e pequenas rotações, mantendo as partes turquesa dentro da asa preta.
    Coordenadas no espaço do carro (origem ~ centro do carro).
    """
    base_y = WHEEL_RADIUS - 0.20
    base_z = FRONT_WING_Z

    MAIN_SPAN   = CAR_WIDTH * 1.30     # envergadura do plano principal (preto)
    MAIN_DEPTH  = 0.85
    FLAP_THICK  = 0.025

    # ----------------- PLANO PRINCIPAL PRETO -----------------
    glPushMatrix()
    glTranslatef(0.0, base_y, base_z)
    glColor3f(*BLACK_MAIN)
    draw_box(MAIN_SPAN, 0.05, MAIN_DEPTH)
    glPopMatrix()

    # limite interno para os flaps ficarem "dentro" da asa preta
    half_main = MAIN_SPAN / 2.0
    margin    = 0.03  # folguinha pra não encostar na borda

    # ----------------- FLAPS CURVOS PETRONAS -----------------
    for side in (-1, 1):
        side_sign = float(side)

        for i in range(4):
            # 0 = mais interno, 3 = mais externo
            t = i / 3.0

            span  = (MAIN_SPAN * 0.32) * (1.0 - 0.10 * i)  # um pouco mais estreito
            depth = 0.45

            # posição em Z/Y (curvando para trás e subindo)
            y = base_y + 0.03 + 0.03 * i
            z = base_z + 0.05 + 0.06 * i

            # coloca o centro do flap justo antes da borda interna preta,
            # garantindo que span/2 + margem não ultrapasse
            center_x = side_sign * (half_main - margin - span / 2.0)

            # ângulos para dar "curva" e ataque
            attack_angle = -8.0 - 6.0 * t         # inclinação em torno de X
            sweep_angle  = 4.0 * side_sign * t    # leve torcida em torno de Z

            glPushMatrix()
            glTranslatef(center_x, y, z)
            glRotatef(sweep_angle, 0, 0, 1)
            glRotatef(attack_angle, 1, 0, 0)
            glColor3f(*PETRONAS_TEAL)
            draw_box(span, FLAP_THICK, depth)
            glPopMatrix()

    # ----------------- “CANARDS” CENTRAIS TEAL -----------------
    for i in range(2):
        z_off = base_z + 0.10 + i * 0.16
        glPushMatrix()
        glTranslatef(0.0, base_y + 0.02 + i * 0.02, z_off)
        glRotatef(-10.0, 1, 0, 0)
        glColor3f(*PETRONAS_TEAL)
        draw_box(CAR_WIDTH * 0.45, FLAP_THICK, 0.35)
        glPopMatrix()

    # ----------------- ENDPLATES COM DETALHE TEAL -----------------
    ENDPLATE_HEIGHT = 0.22
    ENDPLATE_DEPTH  = 0.65
    ENDPLATE_THICK  = 0.06

    for side in (-1, 1):
        side_sign = float(side)
        x = side_sign * (MAIN_SPAN / 2.0 - ENDPLATE_THICK / 2.0)
        y = base_y + ENDPLATE_HEIGHT / 2.0
        z = base_z + 0.10

        # placa preta levemente inclinada pra fora
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(6.0 * side_sign, 0, 1, 0)
        glColor3f(*BLACK_MAIN)
        draw_box(ENDPLATE_THICK, ENDPLATE_HEIGHT, ENDPLATE_DEPTH)
        glPopMatrix()

        # faixa teal na borda superior
        glPushMatrix()
        glTranslatef(x,
                     y + ENDPLATE_HEIGHT / 2.0 + 0.01,
                     z + ENDPLATE_DEPTH * 0.10)
        glRotatef(6.0 * side_sign, 0, 1, 0)
        glColor3f(*PETRONAS_LIGHT)
        draw_box(ENDPLATE_THICK * 1.02, 0.03, ENDPLATE_DEPTH * 0.50)
        glPopMatrix()

def draw_floor():
    """
    Assoalho com formato mais coerente:
    - plank central estreito
    - piso lateral mais largo sob os sidepods e afunilando atrás
    - difusor curto logo depois do eixo traseiro
    """
    base_y = WHEEL_RADIUS - 0.20  # um pouco acima da pista

    # --------- PLANK CENTRAL (madeira) ----------
    plank_length = CAR_LENGTH * 0.85
    plank_width  = CAR_WIDTH * 0.25
    plank_z      = (FRONT_AXLE_Z + REAR_AXLE_Z) / 2.0 + 0.1

    glPushMatrix()
    glTranslatef(0.0, base_y - PLANK_THICK / 2.0, plank_z)
    glColor3f(*PLANK_BROWN)
    draw_box(plank_width, PLANK_THICK, plank_length)
    glPopMatrix()

    # --------- PISO LATERAL FRONTAL (região entrada de ar) ----------
    front_len   = 1.8
    front_width = CAR_WIDTH * 1.05
    front_z     = FRONT_AXLE_Z + front_len / 2.0 + 0.25   # vai até mais ou menos o centro do carro

    glPushMatrix()
    glTranslatef(0.0, base_y, front_z)
    glColor3f(*BLACK_PLANK)
    draw_box(front_width, PLANK_THICK, front_len)
    glPopMatrix()

    # --------- PISO LATERAL CENTRAL (sob os sidepods) ----------
    mid_len   = 1.9
    mid_width = CAR_WIDTH * 1.15          # mais largo na parte média
    mid_z     = 0.55                      # ali na região dos sidepods

    glPushMatrix()
    glTranslatef(0.0, base_y, mid_z)
    glColor3f(*BLACK_PLANK)
    draw_box(mid_width, PLANK_THICK, mid_len)
    glPopMatrix()

    # --------- PISO LATERAL TRASEIRO (afunilando) ----------
    rear_len   = 1.4
    rear_width = CAR_WIDTH * 0.90         # mais estreito na traseira
    # termina POUCO depois do eixo traseiro
    rear_center_end = REAR_AXLE_Z + 0.4   # fim ~2.2
    rear_z          = rear_center_end - rear_len / 2.0

    glPushMatrix()
    glTranslatef(0.0, base_y, rear_z)
    glColor3f(*BLACK_PLANK)
    draw_box(rear_width, PLANK_THICK, rear_len)
    glPopMatrix()

    # --------- BORDAS TEAL (só na parte central do assoalho) ----------
    edge_len   = mid_len * 0.85
    edge_width = 0.06
    edge_z     = mid_z

    for side in (-1, 1):
        side_sign = float(side)
        x = side_sign * (mid_width / 2.0 - edge_width / 2.0)

        glPushMatrix()
        glTranslatef(x, base_y + 0.001, edge_z)
        glColor3f(*PETRONAS_TEAL)
        draw_box(edge_width, 0.01, edge_len)
        glPopMatrix()

    # --------- DIFUSOR CURTO NA TRASEIRA ----------
    diff_len   = 0.6
    diff_width = rear_width * 0.95
    # começa logo atrás do eixo traseiro e termina antes da asa
    diff_z     = REAR_AXLE_Z + 0.45

    glPushMatrix()
    glTranslatef(0.0, base_y + 0.05, diff_z)
    glRotatef(-12.0, 1, 0, 0)  # sobe a parte de trás
    glColor3f(*BLACK_PLANK)
    draw_box(diff_width, PLANK_THICK, diff_len)
    glPopMatrix()

def draw_wishbone(p_inner, p_outer, y, thickness=0.03):
    """
    Desenha uma haste (wishbone) entre dois pontos (x,z),
    na altura y, com pequena espessura.
    p_inner, p_outer = (x, z)
    """
    x1, z1 = p_inner
    x2, z2 = p_outer

    dx = x2 - x1
    dz = z2 - z1
    length = math.sqrt(dx*dx + dz*dz)
    if length <= 0:
        return

    # ângulo em torno do eixo Y (no plano XZ)
    angle_y = math.degrees(math.atan2(dx, dz))

    cx = (x1 + x2) / 2.0
    cz = (z1 + z2) / 2.0

    glPushMatrix()
    glTranslatef(cx, y, cz)
    glRotatef(angle_y, 0, 1, 0)
    glColor3f(0.03, 0.03, 0.03)  # suspensão bem preta
    draw_box(length, thickness, thickness)
    glPopMatrix()

# ----------------- CARRO (MERCEDES W12 SIMPLIFICADA) -----------------

def draw_car(wheel_angle, drs_open):
    """
    ...
    """
    # 1) Assoalho completo (plank + laterais + difusor)
    draw_floor()
    # =====================================================
    # 2) CHASSIS PRINCIPAL (FRONTAL + TRASEIRO)
    # =====================================================
    CHASSIS_HEIGHT = 0.32
    FRONT_CHASSIS_LEN = 2.1
    REAR_CHASSIS_LEN  = 2.0

    FRONT_CHASSIS_WIDTH = CAR_WIDTH * 0.55
    REAR_CHASSIS_WIDTH  = CAR_WIDTH * 0.75

    # trecho frontal
    glPushMatrix()
    glTranslatef(
        0.0,
        WHEEL_RADIUS - 0.18 + PLANK_THICK + CHASSIS_HEIGHT / 2.0,
        FRONT_AXLE_Z + 0.3
    )
    glColor3f(*BLACK_MAIN)
    draw_box(FRONT_CHASSIS_WIDTH, CHASSIS_HEIGHT, FRONT_CHASSIS_LEN)
    glPopMatrix()

    # trecho traseiro (motor)
    glPushMatrix()
    glTranslatef(
        0.0,
        WHEEL_RADIUS - 0.18 + PLANK_THICK + CHASSIS_HEIGHT / 2.0,
        0.6
    )
    glColor3f(*BLACK_MAIN)
    draw_box(REAR_CHASSIS_WIDTH, CHASSIS_HEIGHT, REAR_CHASSIS_LEN)
    glPopMatrix()

        # =====================================================
    # 3) NARIZ REFINADO ENTRE SUSPENSÃO E ASA
    # =====================================================
    # Altura base do nariz em relação ao chão
    nose_base_y = WHEEL_RADIUS - 0.18 + PLANK_THICK

    # --- "cape" sob o nariz (placa preta logo acima da asa) ---
    glPushMatrix()
    glTranslatef(0.0, nose_base_y - 0.02, FRONT_WING_Z + 0.50)
    glColor3f(*BLACK_MAIN)
    draw_box(CAR_WIDTH * 0.55, 0.04, 0.90)
    glPopMatrix()

    # --- trecho intermediário do nariz (entre suspensão e asa) ---
    # parte que passa entre as hastes da suspensão
    mid_nose_len   = 1.10
    mid_nose_width = CAR_WIDTH * 0.26
    mid_nose_h     = 0.22

    glPushMatrix()
    glTranslatef(
        0.0,
        nose_base_y + mid_nose_h / 2.0 + 0.03,
        FRONT_AXLE_Z + 0.25
    )
    glColor3f(*BLACK_MAIN)
    draw_box(mid_nose_width, mid_nose_h, mid_nose_len)
    glPopMatrix()

    # --- ponta do nariz (mais fina e mais baixa, perto da asa) ---
    tip_nose_len   = 0.95
    tip_nose_width = CAR_WIDTH * 0.18
    tip_nose_h     = 0.20

    glPushMatrix()
    glTranslatef(
        0.0,
        nose_base_y + tip_nose_h / 2.0 - 0.02,   # ligeira queda em relação ao trecho do meio
        FRONT_WING_Z + 0.70
    )
    glColor3f(*BLACK_MAIN)
    draw_box(tip_nose_width, tip_nose_h, tip_nose_len)
    glPopMatrix()

    # --- pilares que ligam o nariz à asa (dois suportes) ---
    for side in (-1, 1):
        side_sign = float(side)
        pillar_x = side_sign * (tip_nose_width / 2.0 - 0.03)

        glPushMatrix()
        glTranslatef(
            pillar_x,
            nose_base_y + 0.05,
            FRONT_WING_Z + 0.65
        )
        glColor3f(*BLACK_MAIN)
        draw_box(0.06, 0.16, 0.35)
        glPopMatrix()

    # --- faixa PETRONAS sob o nariz (detalhe em turquesa) ---
    glPushMatrix()
    glTranslatef(0.0, nose_base_y - 0.03, FRONT_WING_Z + 0.55)
    glColor3f(*PETRONAS_TEAL)
    draw_box(CAR_WIDTH * 0.40, 0.02, 0.70)
    glPopMatrix()

    # =====================================================
    # 4) COCKPIT / TAPA DO PILOTO
    # =====================================================
    COCKPIT_LEN   = 1.25
    COCKPIT_WIDTH = CAR_WIDTH * 0.52
    COCKPIT_H     = 0.30

    glPushMatrix()
    glTranslatef(
        0.0,
        WHEEL_RADIUS - 0.18 + PLANK_THICK + CHASSIS_HEIGHT + COCKPIT_H / 2.0,
        -0.5
    )
    glColor3f(*BLACK_MAIN)
    draw_box(COCKPIT_WIDTH, COCKPIT_H, COCKPIT_LEN)
    glPopMatrix()

    # faixas prata laterais (AMG)
    for side in (-1, 1):
        glPushMatrix()
        glTranslatef(
            (COCKPIT_WIDTH / 2.0 - 0.02) * side,
            WHEEL_RADIUS - 0.18 + PLANK_THICK + CHASSIS_HEIGHT + COCKPIT_H / 2.0,
            -0.5
        )
        glColor3f(*SILVER_STRIPE)
        draw_box(0.03, 0.06, 0.80)
        glPopMatrix()

    # tampo superior levemente prateado (região "estrelinhas AMG")
    glPushMatrix()
    glTranslatef(
        0.0,
        WHEEL_RADIUS - 0.18 + PLANK_THICK + CHASSIS_HEIGHT + COCKPIT_H + 0.01,
        -0.5
    )
    glColor3f(*DARK_GREY)
    draw_box(COCKPIT_WIDTH * 1.05, 0.02, COCKPIT_LEN * 1.1)
    glPopMatrix()

    # =====================================================
    # 5) HALO
    # =====================================================
    halo_y = (WHEEL_RADIUS - 0.18 + PLANK_THICK +
              CHASSIS_HEIGHT + COCKPIT_H + 0.06)

    glColor3f(*BLACK_MAIN)
    # poste central
    glPushMatrix()
    glTranslatef(0.0, halo_y - 0.18, -0.7)
    draw_box(0.08, 0.30, 0.08)
    glPopMatrix()

    # postes laterais
    for side in (-1, 1):
        glPushMatrix()
        glTranslatef(
            (COCKPIT_WIDTH / 2.0 - 0.06) * side,
            halo_y - 0.10,
            -0.25
        )
        draw_box(0.08, 0.40, 0.08)
        glPopMatrix()

    # arco superior
    glPushMatrix()
    glTranslatef(0.0, halo_y + 0.04, -0.35)
    draw_box(COCKPIT_WIDTH + 0.30, 0.08, 0.10)
    glPopMatrix()

    # =====================================================
    # 6) ENTRADA DE AR (INEOS) + TAMPA DO MOTOR
    # =====================================================
    AIRBOX_WIDTH  = 0.50
    AIRBOX_HEIGHT = 0.35
    AIRBOX_LEN    = 0.55

    # base preta
    glPushMatrix()
    glTranslatef(0.0, halo_y + 0.18, -0.1)
    glColor3f(*BLACK_MAIN)
    draw_box(AIRBOX_WIDTH, AIRBOX_HEIGHT * 0.6, AIRBOX_LEN)
    glPopMatrix()

    # topo vermelho INEOS
    glPushMatrix()
    glTranslatef(0.0, halo_y + 0.18 + AIRBOX_HEIGHT * 0.35, -0.1)
    glColor3f(*INEOS_RED)
    draw_box(AIRBOX_WIDTH * 0.85, AIRBOX_HEIGHT * 0.35, AIRBOX_LEN * 0.9)
    glPopMatrix()

    # "shark fin" preta
    glPushMatrix()
    glTranslatef(0.0, halo_y + 0.05, 1.1)
    glColor3f(*BLACK_MAIN)
    draw_box(0.10, 0.70, 2.0)
    glPopMatrix()

    # =====================================================
    # 7) SIDEPODS COM UNDERCUT + FAIXA PETRONAS
    # =====================================================
    SIDEPOD_LEN   = 1.8
    SIDEPOD_H     = 0.45
    SIDEPOD_WIDTH = 0.70

    for side in (-1, 1):
        # bloco principal
        glPushMatrix()
        glTranslatef(
            side * (CAR_WIDTH / 2.0 - SIDEPOD_WIDTH / 2.0),
            WHEEL_RADIUS - 0.18 + PLANK_THICK + SIDEPOD_H / 2.0,
            0.3
        )
        glColor3f(*BLACK_MAIN)
        draw_box(SIDEPOD_WIDTH, SIDEPOD_H, SIDEPOD_LEN)
        glPopMatrix()

        # undercut
        glPushMatrix()
        glTranslatef(
            side * (CAR_WIDTH / 2.0 - SIDEPOD_WIDTH / 2.0),
            WHEEL_RADIUS - 0.18 + PLANK_THICK + SIDEPOD_H / 2.0 - 0.18,
            -0.1
        )
        glColor3f(*BLACK_MAIN)
        draw_box(SIDEPOD_WIDTH * 0.9, SIDEPOD_H * 0.6, SIDEPOD_LEN * 0.8)
        glPopMatrix()

        # faixa teal principal
        glPushMatrix()
        glTranslatef(
            side * (CAR_WIDTH / 2.0 - SIDEPOD_WIDTH + 0.05),
            WHEEL_RADIUS - 0.18 + PLANK_THICK + 0.15,
            0.25
        )
        glColor3f(*PETRONAS_TEAL)
        draw_box(0.05, 0.18, 1.4)
        glPopMatrix()

        # filete branco fino em cima da faixa teal
        glPushMatrix()
        glTranslatef(
            side * (CAR_WIDTH / 2.0 - SIDEPOD_WIDTH + 0.055),
            WHEEL_RADIUS - 0.18 + PLANK_THICK + 0.26,
            0.25
        )
        glColor3f(*WHITE_SPONSOR)
        draw_box(0.01, 0.03, 1.35)
        glPopMatrix()

    # =====================================================
    # 8) ASA DIANTEIRA MULTI-ELEMENTO (PETRONAS)
    # =====================================================
    draw_front_wing()
    # =====================================================
    # 9) ASA TRASEIRA + DRS (PETRONAS)
    # =====================================================
    REAR_WING_WIDTH = CAR_WIDTH * 0.95

    # endplates pretos com faixa teal
    for side in (-1, 1):
        glPushMatrix()
        glTranslatef(
            side * (REAR_WING_WIDTH / 2.0 - 0.03),
            WHEEL_RADIUS + 0.60,
            REAR_WING_Z
        )
        glColor3f(*BLACK_MAIN)
        draw_box(0.06, 0.80, 0.18)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(
            side * (REAR_WING_WIDTH / 2.0 - 0.025),
            WHEEL_RADIUS + 0.85,
            REAR_WING_Z + 0.02
        )
        glColor3f(*PETRONAS_TEAL)
        draw_box(0.02, 0.30, 0.20)
        glPopMatrix()

    # suporte central
    glPushMatrix()
    glTranslatef(0.0, WHEEL_RADIUS + 0.60, REAR_AXLE_Z + 0.25)
    glColor3f(*BLACK_MAIN)
    draw_box(0.10, 0.75, 0.12)
    glPopMatrix()

    # plano principal preto
    glPushMatrix()
    glTranslatef(0.0, WHEEL_RADIUS + 1.00, REAR_WING_Z)
    glColor3f(*BLACK_MAIN)
    draw_box(REAR_WING_WIDTH, 0.16, 0.35)
    glPopMatrix()

    # flap DRS teal
    drs_angle = 22.0 if drs_open else 0.0
    glPushMatrix()
    glTranslatef(0.0, WHEEL_RADIUS + 1.05, REAR_WING_Z - 0.10)
    glRotatef(drs_angle, 1, 0, 0)
    glTranslatef(0.0, 0.0, 0.25)
    glColor3f(*PETRONAS_TEAL)
    draw_box(REAR_WING_WIDTH - 0.10, 0.12, 0.28)
    glPopMatrix()

    # =====================================================
    # 10) RODAS
    # =====================================================
       # =====================================================
    # 10) RODAS
    # =====================================================
    glColor3f(0.02, 0.02, 0.02)
    wheel_offset_x = CAR_WIDTH / 2.0 - 0.10

    # posições das rodas
    front_right = ( wheel_offset_x, WHEEL_RADIUS, FRONT_AXLE_Z)
    front_left  = (-wheel_offset_x, WHEEL_RADIUS, FRONT_AXLE_Z)
    rear_right  = ( wheel_offset_x, WHEEL_RADIUS, REAR_AXLE_Z)
    rear_left   = (-wheel_offset_x, WHEEL_RADIUS, REAR_AXLE_Z)

    for (x, y, z) in (front_right, front_left, rear_right, rear_left):
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(wheel_angle, 1, 0, 0)
        draw_cylinder(radius=WHEEL_RADIUS, length=WHEEL_WIDTH, segments=24)
        glPopMatrix()

    # =====================================================
    # 11) SUSPENSÃO (HASTES EM V)
    # =====================================================
    # alturas das hastes (superior e inferior)
    susp_y_upper = WHEEL_RADIUS + 0.05
    susp_y_lower = WHEEL_RADIUS - 0.05

    # ponto de ancoragem no chassi (um pouco pra dentro e mais à frente)
    for side in (-1, 1):
        side_sign = float(side)

        # ----------------- EIXO DIANTEIRO -----------------
        # ponto interno no chassi
        front_inner_upper = (side_sign * (CAR_WIDTH * 0.30), FRONT_AXLE_Z + 0.25)
        front_inner_lower = (side_sign * (CAR_WIDTH * 0.32), FRONT_AXLE_Z + 0.10)

        # ponto externo perto da roda
        front_outer = (side_sign * (wheel_offset_x - 0.05), FRONT_AXLE_Z)

        # braço superior em V (lado 1)
        draw_wishbone(front_inner_upper, front_outer, susp_y_upper, thickness=0.025)
        # braço inferior em V (lado 1)
        draw_wishbone(front_inner_lower, front_outer, susp_y_lower, thickness=0.025)

        # ----------------- EIXO TRASEIRO -----------------
        rear_inner_upper = (side_sign * (CAR_WIDTH * 0.28), REAR_AXLE_Z - 0.20)
        rear_inner_lower = (side_sign * (CAR_WIDTH * 0.30), REAR_AXLE_Z - 0.05)

        rear_outer = (side_sign * (wheel_offset_x - 0.05), REAR_AXLE_Z)

        draw_wishbone(rear_inner_upper, rear_outer, susp_y_upper, thickness=0.025)
        draw_wishbone(rear_inner_lower, rear_outer, susp_y_lower, thickness=0.025)



# ----------------- PISTA QUASE INFINITA -----------------

def draw_track():
    """
    Pista longa (quase infinita) no eixo Z.
    Camadas em alturas bem separadas para evitar z-fighting.
    """
    track_width = 10.0
    half_width = track_width / 2.0

    z_min = -2000.0
    z_max =  2000.0

    # Alturas bem separadas
    y_grass   = -0.1   # gramado mais baixo
    y_asphalt = 0.0    # nível da pista
    y_edge    = 0.05   # bordas laterais
    y_center  = 0.06   # faixa central

    # Gramado
    glColor3f(0.0, 0.4, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-30.0, y_grass, z_min)
    glVertex3f( 30.0, y_grass, z_min)
    glVertex3f( 30.0, y_grass, z_max)
    glVertex3f(-30.0, y_grass, z_max)
    glEnd()

    # Asfalto
    glColor3f(0.15, 0.15, 0.15)
    glBegin(GL_QUADS)
    glVertex3f(-half_width, y_asphalt, z_min)
    glVertex3f( half_width, y_asphalt, z_min)
    glVertex3f( half_width, y_asphalt, z_max)
    glVertex3f(-half_width, y_asphalt, z_max)
    glEnd()

    # Bordas brancas laterais
    glColor3f(0.9, 0.9, 0.9)
    edge_width = 0.2
    # direita
    glBegin(GL_QUADS)
    glVertex3f( half_width,             y_edge, z_min)
    glVertex3f( half_width - edge_width,y_edge, z_min)
    glVertex3f( half_width - edge_width,y_edge, z_max)
    glVertex3f( half_width,             y_edge, z_max)
    glEnd()
    # esquerda
    glBegin(GL_QUADS)
    glVertex3f(-half_width,             y_edge, z_min)
    glVertex3f(-half_width + edge_width,y_edge, z_min)
    glVertex3f(-half_width + edge_width,y_edge, z_max)
    glVertex3f(-half_width,             y_edge, z_max)
    glEnd()

    # Faixa central tracejada
    glColor3f(1.0, 1.0, 1.0)
    line_width = 0.25
    segment_length = 4.0
    gap = 4.0
    z = z_min
    while z < z_max:
        glBegin(GL_QUADS)
        glVertex3f(-line_width / 2.0, y_center, z)
        glVertex3f( line_width / 2.0, y_center, z)
        glVertex3f( line_width / 2.0, y_center, z + segment_length)
        glVertex3f(-line_width / 2.0, y_center, z + segment_length)
        glEnd()
        z += segment_length + gap




# ----------------- SETUP OPENGL -----------------
def init_opengl(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width / float(height), 1.0, 5000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.07, 1.0)



# ----------------- LOOP PRINCIPAL -----------------

def main():
    pygame.init()
    pygame.display.set_caption("CG - F1 Mercedes W12 (PyOpenGL + pygame)")

    window_size = [1280, 720]
    screen = pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL | RESIZABLE)
    init_opengl(window_size[0], window_size[1])

    clock = pygame.time.Clock()

    # --- Estado da animação do carro ---
    running = True
    animation_running = False   # controla se o carro está andando ou parado
    animation_finished = False  # fim da animação automática

    car_speed = 0.0          # unidades por segundo
    max_speed = 50.0
    accel = 25.0
    brake_accel = 40.0

    car_z = 0.0              # posição do carro no eixo Z
    travel_distance = 0.0
    max_distance = 1200.0

    wheel_angle = 0.0
    drs_open = False
    steer_angle = 0.0

    # --- Câmera seguindo o carro, mas controlável ---
    camera_yaw = 0.0       # em graus (orbita o carro)
    camera_pitch = -20.0   # em graus
    camera_distance = 10.0
    mouse_sensitivity = 0.15
    zoom_step = 1.0        # quanto o scroll muda o zoom

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    pygame.mouse.get_rel()  # zera delta inicial

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
                    # Toggle: inicia/pausa a animação
                    animation_running = not animation_running
                    if not animation_running:
                        car_speed = 0.0  # para o carro na hora

                elif event.key == K_d:
                    drs_open = not drs_open

            elif event.type == MOUSEWHEEL:
                # Scroll do mouse controla o zoom
                # event.y > 0 = scroll pra frente (aproxima)
                camera_distance -= event.y * zoom_step

        keys = pygame.key.get_pressed()

        # Direção do carro (visual)
        if keys[K_LEFT]:
            steer_angle += 40.0 * dt
        if keys[K_RIGHT]:
            steer_angle -= 40.0 * dt
        steer_angle = max(-20.0, min(20.0, steer_angle))

        # Aceleração/freio manual extra (só quando a animação está rodando)
        if keys[K_UP] and animation_running and not animation_finished:
            car_speed += accel * dt
        if keys[K_DOWN] and animation_running and not animation_finished:
            car_speed -= brake_accel * dt

        # --- Lógica de aceleração automática (início/meio/fim) ---
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

        # Atualiza posição do carro
        distance_step = car_speed * dt
        car_z -= distance_step          # indo para Z negativo
        travel_distance += distance_step

        # Atualiza rotação das rodas
        wheel_circumference = 2.0 * math.pi * WHEEL_RADIUS
        if wheel_circumference > 0:
            wheel_angle += (distance_step / wheel_circumference) * 360.0

        # --- Controle da câmera (orbita o carro) ---
        # Mouse: gira a câmera
        mx, my = pygame.mouse.get_rel()
        camera_yaw   -= mx * mouse_sensitivity
        camera_pitch -= my * mouse_sensitivity

        # Limita pitch para não virar de cabeça pra baixo
        camera_pitch = max(-80.0, min(80.0, camera_pitch))

        # Limita distância do zoom
        camera_distance = max(5.0, min(30.0, camera_distance))

        # Converte yaw/pitch/distância para posição da câmera em torno do carro
        yaw_rad = math.radians(camera_yaw)
        pitch_rad = math.radians(camera_pitch)

        # Ponto que a câmera olha (aprox. centro do carro)
        target_x = 0.0
        target_y = 0.8
        target_z = car_z

        cam_x = target_x + camera_distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        cam_y = target_y + camera_distance * math.sin(pitch_rad)
        cam_z = target_z + camera_distance * math.cos(pitch_rad) * math.cos(yaw_rad)

        # Garante que a câmera não vá abaixo da pista
        cam_y = max(1.0, cam_y)

        # ----------------- DESENHO -----------------
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(
            cam_x, cam_y, cam_z,
            target_x, target_y, target_z,
            0.0, 1.0, 0.0
        )

        # Pista
        draw_track()

        # Carro
        glPushMatrix()
        glTranslatef(0.0, 0.0, car_z)
        glRotatef(steer_angle, 0, 1, 0)
        draw_car(wheel_angle, drs_open)
        glPopMatrix()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
