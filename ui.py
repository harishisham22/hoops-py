"""HUD: scoreboard, controls hint, messages and overlays."""

import pygame

from constants import (
    COLOR_HUD_BG,
    COLOR_HUD_EDGE,
    COLOR_HUD_MUTED,
    COLOR_HUD_TEXT,
    COURT,
    FPS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


def format_clock(frames_left):
    seconds = max(0, (frames_left + FPS - 1) // FPS)
    return f"{seconds // 60}:{seconds % 60:02d}"


class UI:
    def __init__(self):
        self.font_huge = pygame.font.SysFont("arial", 64, bold=True)
        self.font_big = pygame.font.SysFont("arial", 40, bold=True)
        self.font_mid = pygame.font.SysFont("arial", 26, bold=True)
        self.font_small = pygame.font.SysFont("arial", 16, bold=True)

        self.message = ""
        self.message_color = COLOR_HUD_TEXT
        self.message_timer = 0

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------
    def flash(self, text, color=COLOR_HUD_TEXT, frames=90):
        self.message = text
        self.message_color = color
        self.message_timer = frames

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------
    def draw_scoreboard(self, screen, players, scores, frames_left, possession):
        panel = pygame.Rect(COURT.left, 14, COURT.width, 82)
        backdrop = pygame.Surface(panel.size, pygame.SRCALPHA)
        backdrop.fill((*COLOR_HUD_BG, 232))
        screen.blit(backdrop, panel.topleft)
        pygame.draw.rect(screen, COLOR_HUD_EDGE, panel, 2, border_radius=10)

        mid_x = panel.centerx
        pygame.draw.line(
            screen, COLOR_HUD_EDGE, (mid_x - 96, panel.top + 12), (mid_x - 96, panel.bottom - 12), 1
        )
        pygame.draw.line(
            screen, COLOR_HUD_EDGE, (mid_x + 96, panel.top + 12), (mid_x + 96, panel.bottom - 12), 1
        )

        for index, player in enumerate(players):
            is_left = index == 0
            label_y = panel.top + 16
            score_y = panel.top + 45
            margin = 34

            label = self.font_small.render(player.name, True, player.color)
            score = self.font_big.render(str(scores[index]), True, player.color)
            score_rect = score.get_rect()

            if is_left:
                label_rect = label.get_rect(topleft=(panel.left + margin, label_y))
                score_rect.midleft = (panel.left + margin, score_y)
            else:
                label_rect = label.get_rect(topright=(panel.right - margin, label_y))
                score_rect.midright = (panel.right - margin, score_y)

            screen.blit(label, label_rect)
            screen.blit(score, score_rect)

            if possession == index:
                ball_x = label_rect.right + 10 if is_left else label_rect.left - 10
                pygame.draw.circle(screen, player.color, (ball_x, label_rect.centery), 4)
                pygame.draw.circle(
                    screen, (255, 255, 255), (ball_x, label_rect.centery), 4, 1
                )

        time_label = self.font_small.render("TIME", True, COLOR_HUD_MUTED)
        screen.blit(time_label, time_label.get_rect(center=(mid_x, panel.top + 18)))

        clock = self.font_big.render(format_clock(frames_left), True, COLOR_HUD_TEXT)
        screen.blit(clock, clock.get_rect(center=(mid_x, panel.top + 48)))

    def draw_controls(self, screen):
        left = self.font_small.render(
            "P1   A / D move    W jump    S shoot & steal",
            True,
            COLOR_HUD_MUTED,
        )
        right = self.font_small.render(
            "P2   \u2190 / \u2192 move    \u2191 jump    \u2193 shoot & steal",
            True,
            COLOR_HUD_MUTED,
        )
        screen.blit(left, (COURT.left + 8, WINDOW_HEIGHT - 28))
        screen.blit(right, right.get_rect(topright=(COURT.right - 8, WINDOW_HEIGHT - 28)))

    def draw_message(self, screen):
        if self.message_timer <= 0:
            return

        fade = min(255, self.message_timer * 10)
        surface = self.font_huge.render(self.message, True, self.message_color)
        surface.set_alpha(fade)

        shadow = self.font_huge.render(self.message, True, (0, 0, 0))
        shadow.set_alpha(fade // 2)

        rect = surface.get_rect(center=(WINDOW_WIDTH // 2, 250))
        screen.blit(shadow, rect.move(3, 4))
        screen.blit(surface, rect)

    def draw_game_over(self, screen, title, title_color, score_line, subtitle):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 8, 12, 205))
        screen.blit(overlay, (0, 0))

        title_surface = self.font_huge.render(title, True, title_color)
        score_surface = self.font_big.render(score_line, True, COLOR_HUD_TEXT)
        subtitle_surface = self.font_mid.render(subtitle, True, COLOR_HUD_MUTED)

        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 290))
        screen.blit(title_surface, title_rect)
        screen.blit(
            score_surface,
            score_surface.get_rect(center=(WINDOW_WIDTH // 2, 370)),
        )
        screen.blit(
            subtitle_surface,
            subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2, 440)),
        )
