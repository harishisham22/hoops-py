"""A controllable 1v1 basketball player."""

import math

import pygame

from constants import (
    CHARGE_FRAMES,
    COLOR_SKIN,
    COLOR_SKIN_DARK,
    PLAYER_ACCEL,
    PLAYER_FRICTION,
    PLAYER_GRAVITY,
    PLAYER_HEIGHT,
    PLAYER_JUMP_SPEED,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    PUMP_FAKE_FRAMES,
    SHOT_ANGLE_PROFILE,
    SHOT_MAX_POWER,
    SHOT_MIN_POWER,
)


class Player:
    def __init__(self, x, floor_y, color, dark_color, attack_dir, name):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.color = color
        self.dark_color = dark_color
        self.attack_dir = attack_dir
        self.name = name
        self.floor_y = floor_y

        self.x = float(x)
        self.y = float(floor_y - self.height)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.facing = attack_dir
        self.on_ground = True

        self.has_ball = False
        self.charging = False
        self.charge = 0.0
        self.pump_timer = 0
        self.released_shot = False
        self.steal_cooldown = 0
        self.swat_timer = 0

        self.walk_phase = 0.0
        self.dribble_phase = 0.0

        number_font = pygame.font.SysFont("arial", 15, bold=True)
        self.number_surface = number_font.render(
            "1" if attack_dir > 0 else "2", True, (255, 255, 255)
        )

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def center_x(self):
        return self.x + self.width / 2

    def place(self, x):
        self.x = float(x)
        self.y = float(self.floor_y - self.height)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = True
        self.facing = self.attack_dir
        self.reset_shot()
        self.steal_cooldown = 0
        self.swat_timer = 0

    def reset_shot(self):
        self.charging = False
        self.charge = 0.0
        self.pump_timer = 0
        self.released_shot = False

    def pump_fake(self):
        """Raise the ball like a shot, then pull it back without releasing."""
        if not self.has_ball or self.charging or self.pump_timer > 0:
            return False
        self.pump_timer = PUMP_FAKE_FRAMES
        return True

    def ball_anchor(self):
        """Where the ball sits while this player is holding it."""
        cx = self.center_x
        if self.pump_timer > 0:
            return cx + self.facing * 6, self.y - 9
        if self.charging:
            return cx + self.facing * 6, self.y - 6
        bob = math.sin(self.dribble_phase) * 5
        return cx + self.facing * 20, self.y + 38 + bob

    def aim_velocity(self, target_x, from_x):
        """Shot velocity aimed at a hoop, with charge controlling the arc."""
        power = SHOT_MIN_POWER + (SHOT_MAX_POWER - SHOT_MIN_POWER) * self.charge
        distance = abs(target_x - from_x)
        angle = math.radians(self._shot_angle(distance))
        direction = 1 if target_x >= from_x else -1
        return pygame.Vector2(
            direction * power * math.cos(angle),
            -power * math.sin(angle),
        )

    @staticmethod
    def _shot_angle(distance):
        profile = SHOT_ANGLE_PROFILE
        if distance <= profile[0][0]:
            return profile[0][1]
        for (d0, a0), (d1, a1) in zip(profile, profile[1:]):
            if distance <= d1:
                t = (distance - d0) / (d1 - d0)
                return a0 + (a1 - a0) * t
        return profile[-1][1]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, inp, court_rect):
        self.released_shot = False
        self.pump_timer = max(0, self.pump_timer - 1)
        self.steal_cooldown = max(0, self.steal_cooldown - 1)
        self.swat_timer = max(0, self.swat_timer - 1)

        target_speed = 0.0
        if inp.left:
            target_speed -= PLAYER_SPEED
        if inp.right:
            target_speed += PLAYER_SPEED
        if self.charging:
            target_speed *= 0.45

        if target_speed == 0:
            self.vel_x *= PLAYER_FRICTION
            if abs(self.vel_x) < 0.15:
                self.vel_x = 0.0
        else:
            step = PLAYER_ACCEL if target_speed > self.vel_x else -PLAYER_ACCEL
            self.vel_x += step
            if (step > 0 and self.vel_x > target_speed) or (
                step < 0 and self.vel_x < target_speed
            ):
                self.vel_x = target_speed

        if self.has_ball:
            self.facing = self.attack_dir
        elif self.vel_x:
            self.facing = 1 if self.vel_x > 0 else -1

        if inp.jump and self.on_ground:
            self.vel_y = PLAYER_JUMP_SPEED
            self.on_ground = False

        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y = min(self.vel_y + PLAYER_GRAVITY, 22.0)

        if self.x < court_rect.left:
            self.x = float(court_rect.left)
            self.vel_x = 0.0
        if self.x + self.width > court_rect.right:
            self.x = float(court_rect.right - self.width)
            self.vel_x = 0.0

        if self.y + self.height >= court_rect.bottom:
            self.y = float(court_rect.bottom - self.height)
            self.vel_y = 0.0
            self.on_ground = True

        if self.on_ground:
            self.walk_phase += abs(self.vel_x) * 0.14
        if self.has_ball:
            self.dribble_phase += 0.22

        self._update_shot(inp)

    def _update_shot(self, inp):
        if not self.has_ball:
            self.charging = False
            self.charge = 0.0
            return

        if self.pump_timer > 0:
            # The fake holds the ball up, so a shot input during it is ignored.
            self.charging = False
            self.charge = 0.0
            return

        if inp.shoot_down:
            self.charging = True
            self.charge = min(1.0, self.charge + 1.0 / CHARGE_FRAMES)
        elif self.charging:
            # The game consumes this flag and turns it into a shot.
            self.released_shot = True

    def swat(self):
        self.swat_timer = 14

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, screen):
        x = int(self.x)
        y = int(self.y)
        cx = x + self.width // 2
        bottom = y + self.height
        head_y = y + 12
        hip_y = y + 63

        self._draw_shadow(screen, cx)
        if self.has_ball:
            self._draw_possession_ring(screen, cx)

        # Legs
        swing = math.sin(self.walk_phase) * (10 if self.on_ground else 5)
        if not self.on_ground:
            foot_left, foot_right = cx - 9, cx + 9
        else:
            foot_left, foot_right = cx - 7 - swing, cx + 7 + swing

        for hip_offset, foot_x in ((-7, foot_left), (7, foot_right)):
            pygame.draw.line(
                screen,
                COLOR_SKIN_DARK,
                (cx + hip_offset, hip_y),
                (foot_x, bottom - 4),
                7,
            )
            pygame.draw.line(
                screen,
                self.dark_color,
                (foot_x - 5, bottom - 3),
                (foot_x + 5, bottom - 3),
                5,
            )

        # Shorts and jersey
        shorts = pygame.Rect(x + 4, y + 51, self.width - 8, 17)
        pygame.draw.rect(screen, self.dark_color, shorts, border_radius=4)

        torso = pygame.Rect(x + 3, y + 20, self.width - 6, 35)
        pygame.draw.rect(screen, self.color, torso, border_radius=6)
        pygame.draw.rect(screen, self.dark_color, torso, 2, border_radius=6)

        # Number
        screen.blit(
            self.number_surface,
            self.number_surface.get_rect(center=(cx, y + 38)),
        )

        self._draw_arms(screen, cx, y)

        # Head
        pygame.draw.circle(screen, COLOR_SKIN, (cx, head_y), 11)
        pygame.draw.circle(screen, COLOR_SKIN_DARK, (cx, head_y), 11, 1)
        pygame.draw.rect(screen, self.color, (cx - 11, head_y - 8, 22, 5), border_radius=2)
        pygame.draw.circle(screen, (38, 34, 34), (cx + self.facing * 5, head_y + 1), 2)

        if self.charging:
            self._draw_charge_bar(screen, cx, y)

    def _draw_shadow(self, screen, cx):
        jump_height = max(0.0, self.floor_y - (self.y + self.height))
        shrink = min(12.0, jump_height / 12.0)
        width = max(16, 34 - shrink)
        height = max(4, 9 - shrink / 3)
        shadow = pygame.Rect(0, 0, int(width), int(height))
        shadow.center = (cx, int(self.floor_y) - 2)
        pygame.draw.ellipse(screen, (146, 96, 56), shadow)

    def _draw_possession_ring(self, screen, cx):
        pulse = 2 + int((math.sin(self.dribble_phase * 2) + 1) * 1.5)
        ring = pygame.Rect(0, 0, 28 + pulse * 2, 9 + pulse)
        ring.center = (cx, int(self.floor_y) - 3)
        pygame.draw.ellipse(screen, self.color, ring, 2)

    def _draw_arms(self, screen, cx, y):
        shoulder_y = y + 27
        left_shoulder = (cx - 8, shoulder_y)
        right_shoulder = (cx + 8, shoulder_y)

        if self.charging or self.pump_timer > 0:
            hand_x, hand_y = self.ball_anchor()
            pygame.draw.line(screen, COLOR_SKIN, left_shoulder, (hand_x - 4, hand_y + 4), 5)
            pygame.draw.line(screen, COLOR_SKIN, right_shoulder, (hand_x + 4, hand_y + 4), 5)
            pygame.draw.circle(screen, COLOR_SKIN, (int(hand_x - 4), int(hand_y + 4)), 3)
            pygame.draw.circle(screen, COLOR_SKIN, (int(hand_x + 4), int(hand_y + 4)), 3)
            return

        if self.swat_timer > 0:
            hand = (cx + self.facing * 32, shoulder_y + 4)
            pygame.draw.line(screen, COLOR_SKIN, right_shoulder, hand, 5)
            pygame.draw.circle(screen, COLOR_SKIN, (int(hand[0]), int(hand[1])), 3)
            pygame.draw.line(
                screen, COLOR_SKIN, left_shoulder, (cx - self.facing * 6, shoulder_y + 22), 5
            )
            return

        swing = math.sin(self.walk_phase + math.pi) * (8 if self.on_ground else 3)
        pygame.draw.line(
            screen, COLOR_SKIN, left_shoulder, (cx - 12 - swing, y + 50), 5
        )
        pygame.draw.line(
            screen, COLOR_SKIN, right_shoulder, (cx + 12 + swing, y + 50), 5
        )
        pygame.draw.circle(screen, COLOR_SKIN, (int(cx - 12 - swing), y + 50), 3)
        pygame.draw.circle(screen, COLOR_SKIN, (int(cx + 12 + swing), y + 50), 3)

    def _draw_charge_bar(self, screen, cx, y):
        width = 52
        bar = pygame.Rect(cx - width // 2, y - 22, width, 8)
        pygame.draw.rect(screen, (20, 24, 30), bar, border_radius=4)

        ratio = self.charge
        if ratio < 0.5:
            t = ratio / 0.5
            fill_color = (120 + int(115 * t), 220, 110)
        else:
            t = (ratio - 0.5) / 0.5
            fill_color = (235, 220 - int(100 * t), 80)

        fill = bar.inflate(-4, -4)
        fill.width = max(1, int(fill.width * ratio))
        if fill.width > 0:
            pygame.draw.rect(screen, fill_color, fill, border_radius=2)

        pygame.draw.rect(screen, (245, 245, 245), bar, 1, border_radius=4)
