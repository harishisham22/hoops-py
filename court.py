"""The court surface and the two hoops."""

import pygame

from constants import (
    COLOR_APRON,
    COLOR_LINE,
    COLOR_WOOD,
    COLOR_WOOD_LINE,
    COURT,
    THREE_POINT_DISTANCE,
)
from hoop import Hoop


class Court:
    def __init__(self):
        self.rect = COURT.copy()
        self.floor_y = self.rect.bottom
        self.center = pygame.Vector2(self.rect.centerx, self.rect.centery)

        # The left hoop is attacked by player 2, the right hoop by player 1.
        self.left_hoop = Hoop("left", self.rect, owner=1)
        self.right_hoop = Hoop("right", self.rect, owner=0)
        self.hoops = (self.left_hoop, self.right_hoop)

        self._surface = self._build_surface()

    def hoop_for_direction(self, direction):
        """The hoop a player attacks, based on ``Player.attack_dir``."""
        return self.right_hoop if direction > 0 else self.left_hoop

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, screen):
        screen.blit(self._surface, self.rect.topleft)
        for hoop in self.hoops:
            hoop.draw(screen)

    def _build_surface(self):
        w, h = self.rect.size
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        surface.fill(COLOR_WOOD)

        # Out-of-bounds apron at the bottom and plank lines across the floor.
        pygame.draw.rect(surface, COLOR_APRON, (0, h - 14, w, 14))
        for y in range(0, h, 44):
            pygame.draw.line(surface, COLOR_WOOD_LINE, (0, y), (w, y), 1)
        for x in range(0, w, 160):
            pygame.draw.line(surface, (194, 134, 82), (x, 0), (x, h), 1)

        # Transparent court paint is drawn on its own surface so the blit
        # blends it with the wood instead of punching holes in the court.
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        self._draw_key(overlay, 0, 190)
        self._draw_key(overlay, w - 190, 190)
        self._draw_markings(overlay)
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, COLOR_LINE, surface.get_rect(), 4)
        return surface

    def _draw_key(self, surface, left, width):
        h = surface.get_height()
        key = pygame.Rect(left, h - 150, width, 150)
        pygame.draw.rect(surface, (16, 48, 78, 120), key)
        pygame.draw.rect(surface, (248, 244, 235, 150), key, 3)

        # Free-throw line tick on top of the key.
        pygame.draw.line(
            surface,
            (248, 244, 235, 150),
            (key.centerx - 20, key.top),
            (key.centerx + 20, key.top),
            3,
        )

    def _draw_markings(self, surface):
        w, h = surface.get_size()
        line_top = h - 210
        center_x = w // 2

        # Half-court line and centre circle.
        self._dashed_line(surface, center_x, line_top, h - 14)
        circle = pygame.Rect(0, 0, 190, 66)
        circle.center = (center_x, h - 34)
        pygame.draw.ellipse(surface, (245, 240, 230, 105), circle, 2)

        # Three-point marks, measured from each rim.
        left_three = self.left_hoop.center_x - self.rect.left + THREE_POINT_DISTANCE
        right_three = self.right_hoop.center_x - self.rect.left - THREE_POINT_DISTANCE
        font = pygame.font.SysFont("arial", 13, bold=True)
        for x in (int(left_three), int(right_three)):
            self._dashed_line(surface, x, line_top, h - 14)
            pygame.draw.circle(surface, (245, 240, 230, 120), (x, h - 14), 3)
            label = font.render("3PT", True, (250, 246, 238))
            surface.blit(label, label.get_rect(center=(x, line_top - 12)))

    @staticmethod
    def _dashed_line(surface, x, top, bottom, dash=12, gap=9):
        y = top
        while y < bottom:
            pygame.draw.line(
                surface,
                (245, 240, 230, 110),
                (x, y),
                (x, min(y + dash, bottom)),
                2,
            )
            y += dash + gap
