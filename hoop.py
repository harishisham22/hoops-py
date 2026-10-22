"""A single basketball hoop: backboard, rim, net and score detection."""

import pygame

from constants import (
    BACKBOARD_HEIGHT,
    BACKBOARD_MARGIN,
    BACKBOARD_WIDTH,
    COLOR_BACKBOARD,
    COLOR_BACKBOARD_EDGE,
    COLOR_NET,
    COLOR_RIM,
    COLOR_RIM_LIGHT,
    NET_DEPTH,
    PLAYER_COLORS,
    RIM_LENGTH,
    RIM_POST_RADIUS,
    RIM_Y,
)


class Hoop:
    """One hoop, mounted on the left or right sideline.

    ``owner`` is the index of the player that attacks this hoop.  Points are
    credited to that player, so accidentally scoring in your own basket gives
    the points to your opponent.
    """

    def __init__(self, side, court_rect, owner):
        if side not in ("left", "right"):
            raise ValueError(f"side must be 'left' or 'right', not {side!r}")

        self.side = side
        self.owner = owner
        self.rim_y = RIM_Y
        self.floor_y = court_rect.bottom

        if side == "left":
            board_x = court_rect.left + BACKBOARD_MARGIN
        else:
            board_x = court_rect.right - BACKBOARD_MARGIN - BACKBOARD_WIDTH

        self.backboard = pygame.Rect(
            board_x,
            self.rim_y + 8 - BACKBOARD_HEIGHT,
            BACKBOARD_WIDTH,
            BACKBOARD_HEIGHT,
        )

        if side == "left":
            self.rim_left = self.backboard.right
            self.rim_right = self.rim_left + RIM_LENGTH
        else:
            self.rim_right = self.backboard.left
            self.rim_left = self.rim_right - RIM_LENGTH

        self.center_x = (self.rim_left + self.rim_right) / 2
        self.center = pygame.Vector2(self.center_x, self.rim_y)
        self.posts = (
            pygame.Vector2(self.rim_left, self.rim_y),
            pygame.Vector2(self.rim_right, self.rim_y),
        )

    # ------------------------------------------------------------------
    # Game logic
    # ------------------------------------------------------------------
    def ball_passed_through(self, ball, previous_y):
        """True when the ball drops through the rim between two physics steps."""
        return (
            previous_y < self.rim_y <= ball.y
            and ball.vel.y > 0
            and self.rim_left + 2 < ball.x < self.rim_right - 2
        )

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, screen):
        owner_color = PLAYER_COLORS[self.owner]["main"]
        self._draw_support(screen)
        self._draw_backboard(screen, owner_color)
        self._draw_net(screen)
        self._draw_rim(screen)

    def _draw_support(self, screen):
        board = self.backboard
        x = board.centerx
        top = board.bottom - 6
        pygame.draw.line(screen, (58, 66, 74), (x, top), (x, self.floor_y), 8)
        pygame.draw.line(screen, (92, 102, 112), (x - 1, top), (x - 1, self.floor_y), 3)

    def _draw_backboard(self, screen, owner_color):
        board = self.backboard
        pygame.draw.rect(screen, COLOR_BACKBOARD, board, border_radius=3)
        pygame.draw.rect(screen, COLOR_BACKBOARD_EDGE, board, 2, border_radius=3)

        # Shooter's square painted on the front of the board.
        inner_h = 46
        inner_w = 5
        if self.side == "left":
            square = pygame.Rect(
                board.right - inner_w - 2,
                self.rim_y - inner_h // 2,
                inner_w,
                inner_h,
            )
        else:
            square = pygame.Rect(
                board.left + 2,
                self.rim_y - inner_h // 2,
                inner_w,
                inner_h,
            )

        accent = pygame.Rect(board.left + 2, board.top + 4, board.width - 4, 8)
        pygame.draw.rect(screen, owner_color, square)
        pygame.draw.rect(screen, owner_color, accent, border_radius=2)

    def _draw_rim(self, screen):
        pygame.draw.line(
            screen,
            COLOR_RIM,
            (self.rim_left, self.rim_y),
            (self.rim_right, self.rim_y),
            6,
        )
        pygame.draw.line(
            screen,
            COLOR_RIM_LIGHT,
            (self.rim_left + 2, self.rim_y - 1),
            (self.rim_right - 2, self.rim_y - 1),
            2,
        )
        for post in self.posts:
            pygame.draw.circle(screen, COLOR_RIM, (int(post.x), int(post.y)), RIM_POST_RADIUS)
            pygame.draw.circle(
                screen,
                COLOR_RIM_LIGHT,
                (int(post.x), int(post.y - 1)),
                max(1, RIM_POST_RADIUS - 2),
            )

    def _draw_net(self, screen):
        top_y = self.rim_y + 3
        bottom_y = self.rim_y + NET_DEPTH
        top_left = self.rim_left + 4
        top_right = self.rim_right - 4
        bottom_left = self.center_x - 11
        bottom_right = self.center_x + 11

        def lerp(a, b, t):
            return a + (b - a) * t

        for i in range(7):
            t = i / 6
            pygame.draw.line(
                screen,
                COLOR_NET,
                (lerp(top_left, top_right, t), top_y),
                (lerp(bottom_left, bottom_right, t), bottom_y),
                1,
            )

        for t in (0.45, 0.75):
            y = lerp(top_y, bottom_y, t)
            left = lerp(top_left, bottom_left, t)
            right = lerp(top_right, bottom_right, t)
            pygame.draw.line(screen, COLOR_NET, (left, y), (right, y), 1)
