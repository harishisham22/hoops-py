"""Game loop, rules and orchestration."""

import pygame

from ball import Ball
from constants import (
    BALL_AIR_DRAG,
    BALL_GRAVITY,
    BALL_SUBSTEPS,
    COLOR_BG,
    FPS,
    GAME_SECONDS,
    PLAYER_COLORS,
    SCORE_PAUSE,
    STEAL_COOLDOWN,
    STEAL_RANGE,
    THREE_POINT_DISTANCE,
    THREE_POINT_VALUE,
    TWO_POINT_VALUE,
)
from controls import PLAYER_CONTROLS, read_input
from court import Court
from player import Player
from ui import UI


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.court = Court()
        self.ui = UI()
        self.players = [
            Player(
                self.court.rect.left + self.court.rect.width * 0.24,
                self.court.floor_y,
                PLAYER_COLORS[0]["main"],
                PLAYER_COLORS[0]["dark"],
                attack_dir=1,
                name="PLAYER 1",
            ),
            Player(
                self.court.rect.left + self.court.rect.width * 0.76,
                self.court.floor_y,
                PLAYER_COLORS[1]["main"],
                PLAYER_COLORS[1]["dark"],
                attack_dir=-1,
                name="PLAYER 2",
            ),
        ]
        self.ball = Ball(self.court.rect.centerx, self.court.rect.top + 120)

        self.previous_shoot = [False, False]
        self.previous_pump = [False, False]
        self.scores = [0, 0]
        self.frames_left = GAME_SECONDS * FPS
        self.state = "playing"
        self.pause_timer = 0
        self.winner = None

        self._reset_positions()
        self.ui.flash("TIP OFF!", (255, 255, 255), 90)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            self._handle_events()
            if not self.running:
                break
            self._update(pygame.key.get_pressed())
            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self._start_new_game()

    def _start_new_game(self):
        self.scores = [0, 0]
        self.frames_left = GAME_SECONDS * FPS
        self.state = "playing"
        self.pause_timer = 0
        self.winner = None
        self.previous_shoot = [False, False]
        self.previous_pump = [False, False]
        self._reset_positions()
        self.ui.flash("TIP OFF!", (255, 255, 255), 90)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def _update(self, keys):
        self.ui.update()

        if self.state == "game_over":
            return

        if self.state == "scored":
            self.pause_timer -= 1
            if self.pause_timer <= 0:
                self.state = "playing"
                self._reset_positions()
            return

        # Playing
        self.frames_left -= 1
        if self.frames_left <= 0:
            self._end_game()
            return

        for index, player in enumerate(self.players):
            state, shoot_down, pump_down = read_input(
                keys,
                PLAYER_CONTROLS[index],
                self.previous_shoot[index],
                self.previous_pump[index],
            )
            self.previous_shoot[index] = shoot_down
            self.previous_pump[index] = pump_down

            if state.pump_pressed:
                player.pump_fake()

            player.update(state, self.court.rect)

            if player.released_shot:
                self._shoot(index)
            elif state.shoot_pressed and not player.has_ball:
                player.swat()
                self._attempt_steal(index)

        self._separate_players()
        self.ball.update(self.court.rect, self.court.hoops)

        for hoop in self.ball.scored_hoops:
            self._register_score(hoop)
            break

        if self.state == "playing":
            self._pickup_loose_ball()

    def _shoot(self, index):
        player = self.players[index]
        if not player.has_ball:
            player.reset_shot()
            return

        hoop = self.court.hoop_for_direction(player.attack_dir)
        velocity = player.aim_velocity(hoop.center_x, self.ball.x)
        self.ball.shoot(velocity)
        # The 2/3 point ruling uses the shooter's feet, not the ball's hands.
        self.ball.shot_origin.update(player.center_x, self.ball.y)
        player.has_ball = False
        player.reset_shot()

    def _attempt_steal(self, index):
        player = self.players[index]
        if player.steal_cooldown > 0:
            return

        opponent = self.players[1 - index]
        if not opponent.has_ball:
            return
        if not player.rect.inflate(STEAL_RANGE, 24).colliderect(opponent.rect):
            return

        self._give_ball(player)
        player.steal_cooldown = STEAL_COOLDOWN
        self.ui.flash("STEAL!", player.color, 45)

    def _separate_players(self):
        first, second = self.players
        if not first.rect.colliderect(second.rect):
            return

        overlap = min(
            first.rect.right - second.rect.left,
            second.rect.right - first.rect.left,
        )
        if overlap <= 0:
            return

        push = overlap / 2 + 0.5
        if first.center_x <= second.center_x:
            first.x -= push
            second.x += push
        else:
            first.x += push
            second.x -= push

        court = self.court.rect
        for player in self.players:
            player.x = max(court.left, min(player.x, court.right - player.width))

    def _give_ball(self, player):
        self.ball.attach(player)
        for other in self.players:
            other.has_ball = other is player
            other.reset_shot()

    def _pickup_loose_ball(self):
        ball = self.ball
        if ball.holder is not None or ball.pickup_delay > 0:
            return

        candidates = [p for p in self.players if p.rect.colliderect(ball.rect)]
        if not candidates:
            return

        nearest = min(
            candidates,
            key=lambda p: (p.center_x - ball.x) ** 2
            + (p.y + p.height / 2 - ball.y) ** 2,
        )
        self._give_ball(nearest)

    def _register_score(self, hoop):
        scorer_index = hoop.owner
        scorer = self.players[scorer_index]
        points = (
            THREE_POINT_VALUE
            if self.ball.shot_distance(hoop) >= THREE_POINT_DISTANCE
            else TWO_POINT_VALUE
        )
        self.scores[scorer_index] += points

        self.state = "scored"
        self.pause_timer = SCORE_PAUSE
        self.ball.vel.update(0, 0)
        for player in self.players:
            player.has_ball = False
            player.reset_shot()

        label = "3 POINTER!" if points == THREE_POINT_VALUE else "BUCKET!"
        self.ui.flash(f"{label}  {scorer.name} +{points}", scorer.color, SCORE_PAUSE)

    def _end_game(self):
        self.state = "game_over"
        self.ui.message_timer = 0
        if self.scores[0] == self.scores[1]:
            self.winner = None
        else:
            self.winner = 0 if self.scores[0] > self.scores[1] else 1

    def _reset_positions(self):
        left = self.court.rect.left
        width = self.court.rect.width
        self.players[0].place(left + width * 0.24)
        self.players[1].place(left + width * 0.76)

        for player in self.players:
            player.has_ball = False
            player.reset_shot()
            player.steal_cooldown = 0
            player.swat_timer = 0

        self.ball.reset(self.court.rect.centerx, self.court.rect.top + 180)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def _draw(self):
        self.screen.fill(COLOR_BG)
        self.court.draw(self.screen)

        if self.state == "playing":
            self._draw_shot_preview()

        for player in self.players:
            player.draw(self.screen)
        self.ball.draw(self.screen)

        possession = next(
            (i for i, player in enumerate(self.players) if player.has_ball), None
        )
        self.ui.draw_scoreboard(
            self.screen, self.players, self.scores, self.frames_left, possession
        )
        self.ui.draw_controls(self.screen)
        self.ui.draw_message(self.screen)

        if self.state == "game_over":
            if self.winner is None:
                title = "TIE GAME"
                title_color = (230, 235, 240)
            else:
                winner = self.players[self.winner]
                title = f"{winner.name} WINS!"
                title_color = winner.color

            self.ui.draw_game_over(
                self.screen,
                title,
                title_color,
                f"{self.scores[0]}  -  {self.scores[1]}",
                "Press R to play again",
            )

    def _draw_shot_preview(self):
        for player in self.players:
            if not (player.charging and player.has_ball):
                continue

            hoop = self.court.hoop_for_direction(player.attack_dir)
            position = pygame.Vector2(self.ball.x, self.ball.y)
            velocity = player.aim_velocity(hoop.center_x, position.x)
            color = self._lighten(player.color, 0.4)
            dt = 1.0 / BALL_SUBSTEPS

            for frame in range(70):
                for _ in range(BALL_SUBSTEPS):
                    velocity.y += BALL_GRAVITY * dt
                    position.x += velocity.x * dt
                    position.y += velocity.y * dt
                velocity.x *= BALL_AIR_DRAG
                velocity.y *= BALL_AIR_DRAG

                if frame % 2 == 0:
                    radius = 3 if frame < 24 else 2
                    pygame.draw.circle(
                        self.screen,
                        color,
                        (int(position.x), int(position.y)),
                        radius,
                    )

                if (
                    position.y > self.court.rect.bottom
                    or position.x < self.court.rect.left
                    or position.x > self.court.rect.right
                ):
                    break

    @staticmethod
    def _lighten(color, amount):
        return tuple(min(255, int(c + (255 - c) * amount)) for c in color)
