"""The ball: physics, collisions and rendering."""

import math

import pygame

from constants import (
    BALL_AIR_DRAG,
    BALL_FLOOR_FRICTION,
    BALL_GRAVITY,
    BALL_MAX_SPEED,
    BALL_PICKUP_DELAY,
    BALL_RADIUS,
    BALL_RESTITUTION,
    BALL_SUBSTEPS,
    COLOR_BALL,
    COLOR_BALL_DARK,
    COLOR_BALL_LIGHT,
    RIM_POST_RADIUS,
)


class Ball:
    def __init__(self, x, y, radius=BALL_RADIUS):
        self.radius = radius
        self.x = float(x)
        self.y = float(y)
        self.vel = pygame.Vector2()
        self.holder = None
        self.pickup_delay = 0
        self.shot_origin = pygame.Vector2(x, y)
        self.spin = 0.0
        self.previous_y = self.y
        self.scored_hoops = []

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    @property
    def rect(self):
        r = self.radius
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    @property
    def center(self):
        return pygame.Vector2(self.x, self.y)

    @property
    def is_loose(self):
        return self.holder is None

    def reset(self, x, y):
        self.holder = None
        self.x = float(x)
        self.y = float(y)
        self.vel.update(0, 0)
        self.pickup_delay = 0
        self.shot_origin.update(x, y)
        self.spin = 0.0
        self.previous_y = self.y
        self.scored_hoops = []

    def attach(self, player):
        self.holder = player
        self.vel.update(0, 0)
        self.pickup_delay = 0
        self.scored_hoops = []

    def shoot(self, velocity):
        self.holder = None
        self.vel = pygame.Vector2(velocity)
        if self.vel.length() > BALL_MAX_SPEED:
            self.vel.scale_to_length(BALL_MAX_SPEED)
        self.pickup_delay = BALL_PICKUP_DELAY
        self.shot_origin.update(self.x, self.y)
        self.spin = 0.0
        self.scored_hoops = []

    def shot_distance(self, hoop):
        """Horizontal distance from the last shot to ``hoop``."""
        return abs(self.shot_origin.x - hoop.center_x)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, court_rect, hoops):
        self.scored_hoops = []
        self.previous_y = self.y

        if self.holder is not None:
            self._follow_holder()
            return

        self.pickup_delay = max(0, self.pickup_delay - 1)

        dt = 1.0 / BALL_SUBSTEPS
        for _ in range(BALL_SUBSTEPS):
            step_start_y = self.y
            self.vel.y += BALL_GRAVITY * dt
            self.x += self.vel.x * dt
            self.y += self.vel.y * dt

            for hoop in hoops:
                if hoop.ball_passed_through(self, step_start_y):
                    self.scored_hoops.append(hoop)

            self._collide_hoops(hoops)
            self._collide_bounds(court_rect)

        self.vel.x *= BALL_AIR_DRAG
        self.vel.y *= BALL_AIR_DRAG

        resting_on_floor = self.y + self.radius >= court_rect.bottom - 0.5
        if resting_on_floor and abs(self.vel.y) < 0.5:
            self.vel.x *= BALL_FLOOR_FRICTION
            if abs(self.vel.x) < 0.05:
                self.vel.x = 0.0

        self.spin += self.vel.x * 0.12

    def _follow_holder(self):
        anchor = self.holder.ball_anchor()
        self.x, self.y = anchor
        self.vel.update(0, 0)

    # ------------------------------------------------------------------
    # Collisions
    # ------------------------------------------------------------------
    def _collide_bounds(self, court_rect):
        r = self.radius

        if self.y + r > court_rect.bottom:
            self.y = court_rect.bottom - r
            if self.vel.y > 0:
                self.vel.y = -self.vel.y * BALL_RESTITUTION
                if abs(self.vel.y) < 1.4:
                    self.vel.y = 0.0
                self.vel.x *= 0.96

        if self.y - r < court_rect.top:
            self.y = court_rect.top + r
            if self.vel.y < 0:
                self.vel.y = -self.vel.y * BALL_RESTITUTION

        if self.x - r < court_rect.left:
            self.x = court_rect.left + r
            if self.vel.x < 0:
                self.vel.x = -self.vel.x * BALL_RESTITUTION

        if self.x + r > court_rect.right:
            self.x = court_rect.right - r
            if self.vel.x > 0:
                self.vel.x = -self.vel.x * BALL_RESTITUTION

    def _collide_hoops(self, hoops):
        for hoop in hoops:
            self._collide_rect(hoop.backboard)
            if self.vel.y < 0 and self.y > hoop.rim_y:
                # The rim acts as a one-way gate: a lob rising from below the
                # ring passes through it, then scores (or clangs) on the way
                # down.  Without this, close-range lobs clip the front post on
                # the ascent and drop into an unmakeable dead band.
                continue
            for post in hoop.posts:
                self._collide_circle(post, RIM_POST_RADIUS)

    def _collide_circle(self, point, point_radius):
        dx = self.x - point.x
        dy = self.y - point.y
        min_dist = self.radius + point_radius
        dist_sq = dx * dx + dy * dy
        if dist_sq >= min_dist * min_dist or dist_sq == 0:
            return

        dist = math.sqrt(dist_sq)
        nx, ny = dx / dist, dy / dist
        overlap = min_dist - dist
        self.x += nx * overlap
        self.y += ny * overlap

        vn = self.vel.x * nx + self.vel.y * ny
        if vn < 0:
            self.vel.x -= (1 + BALL_RESTITUTION) * vn * nx
            self.vel.y -= (1 + BALL_RESTITUTION) * vn * ny

    def _collide_rect(self, rect):
        closest_x = min(max(self.x, rect.left), rect.right)
        closest_y = min(max(self.y, rect.top), rect.bottom)
        dx = self.x - closest_x
        dy = self.y - closest_y
        dist_sq = dx * dx + dy * dy
        r = self.radius

        if dist_sq > r * r:
            return

        if dist_sq > 0:
            dist = math.sqrt(dist_sq)
            nx, ny = dx / dist, dy / dist
            overlap = r - dist
            self.x += nx * overlap
            self.y += ny * overlap
        else:
            # Ball centre is inside the rect: pop out through the nearest face.
            to_left = self.x - rect.left
            to_right = rect.right - self.x
            to_top = self.y - rect.top
            to_bottom = rect.bottom - self.y
            smallest = min(to_left, to_right, to_top, to_bottom)
            if smallest == to_left:
                nx, ny = -1.0, 0.0
                self.x = rect.left - r
            elif smallest == to_right:
                nx, ny = 1.0, 0.0
                self.x = rect.right + r
            elif smallest == to_top:
                nx, ny = 0.0, -1.0
                self.y = rect.top - r
            else:
                nx, ny = 0.0, 1.0
                self.y = rect.bottom + r

        vn = self.vel.x * nx + self.vel.y * ny
        if vn < 0:
            self.vel.x -= (1 + BALL_RESTITUTION) * vn * nx
            self.vel.y -= (1 + BALL_RESTITUTION) * vn * ny

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        pygame.draw.circle(screen, COLOR_BALL_DARK, (x, y), self.radius + 1)
        pygame.draw.circle(screen, COLOR_BALL, (x, y), self.radius)

        angle = math.radians(self.spin)
        for base in (0.0, math.pi / 2):
            dx = math.cos(angle + base) * self.radius
            dy = math.sin(angle + base) * self.radius
            pygame.draw.line(
                screen,
                COLOR_BALL_DARK,
                (x - dx, y - dy),
                (x + dx, y + dy),
                2,
            )

        pygame.draw.circle(
            screen,
            COLOR_BALL_LIGHT,
            (x - 4, y - 5),
            max(2, self.radius // 5),
        )
