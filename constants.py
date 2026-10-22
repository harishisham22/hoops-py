"""Shared configuration and tuning values for Hoops 1v1."""

import pygame

# Window ------------------------------------------------------------------
TITLE = "Hoops 1v1"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Court -------------------------------------------------------------------
COURT = pygame.Rect(40, 110, 1200, 570)
FLOOR_Y = COURT.bottom

# Ball --------------------------------------------------------------------
BALL_RADIUS = 13
BALL_GRAVITY = 0.52
BALL_AIR_DRAG = 0.999
BALL_RESTITUTION = 0.62
BALL_FLOOR_FRICTION = 0.985
BALL_MAX_SPEED = 30
BALL_PICKUP_DELAY = 10          # frames a shot ball ignores its shooter
BALL_SUBSTEPS = 2               # keeps fast shots from tunnelling

# Hoops -------------------------------------------------------------------
RIM_Y = 450
RIM_LENGTH = 56
RIM_POST_RADIUS = 4
BACKBOARD_WIDTH = 12
BACKBOARD_HEIGHT = 122
BACKBOARD_MARGIN = 10           # gap between backboard and the sideline wall
NET_DEPTH = 42
THREE_POINT_DISTANCE = 290

# Players -----------------------------------------------------------------
PLAYER_WIDTH = 34
PLAYER_HEIGHT = 78
PLAYER_SPEED = 5.6
PLAYER_ACCEL = 0.9
PLAYER_FRICTION = 0.78
PLAYER_JUMP_SPEED = -14.5
PLAYER_GRAVITY = 0.82
CHARGE_FRAMES = 25              # frames to reach a full-power shot
PUMP_FAKE_FRAMES = 18           # frames the pump-fake animation holds the ball up
SHOT_MIN_POWER = 6.5
SHOT_MAX_POWER = 20.5
# Launch angle eases from a near-vertical lob under the rim to a flatter
# jumper from long range.  (distance from hoop, angle in degrees)
SHOT_ANGLE_PROFILE = (
    (0, 86.0),
    (100, 85.0),
    (200, 80.0),
    (350, 70.0),
    (550, 60.0),
    (800, 54.0),
)
STEAL_RANGE = 46
STEAL_COOLDOWN = 42

# Game rules --------------------------------------------------------------
GAME_SECONDS = 90
SCORE_PAUSE = 85                # celebration frames after a made basket
TWO_POINT_VALUE = 2
THREE_POINT_VALUE = 3

# Colours -----------------------------------------------------------------
COLOR_BG = (14, 20, 28)
COLOR_WOOD = (198, 140, 86)
COLOR_WOOD_DARK = (178, 122, 72)
COLOR_WOOD_LINE = (166, 112, 66)
COLOR_APRON = (150, 98, 58)
COLOR_LINE = (248, 243, 232)
COLOR_LINE_SOFT = (224, 214, 198)
COLOR_HUD_BG = (9, 15, 22)
COLOR_HUD_EDGE = (46, 60, 76)
COLOR_HUD_TEXT = (226, 233, 241)
COLOR_HUD_MUTED = (135, 150, 166)
COLOR_RIM = (240, 88, 52)
COLOR_RIM_LIGHT = (255, 148, 112)
COLOR_BACKBOARD = (228, 236, 244)
COLOR_BACKBOARD_EDGE = (120, 138, 156)
COLOR_NET = (238, 242, 246)
COLOR_BALL = (238, 132, 38)
COLOR_BALL_DARK = (116, 56, 14)
COLOR_BALL_LIGHT = (255, 190, 120)
COLOR_SKIN = (224, 172, 128)
COLOR_SKIN_DARK = (188, 132, 92)

COLOR_BLUE = (58, 132, 240)
COLOR_BLUE_DARK = (30, 82, 168)
COLOR_RED = (230, 72, 72)
COLOR_RED_DARK = (158, 38, 44)

PLAYER_COLORS = (
    {"main": COLOR_BLUE, "dark": COLOR_BLUE_DARK},
    {"main": COLOR_RED, "dark": COLOR_RED_DARK},
)
