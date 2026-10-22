"""Keyboard layouts and per-frame input snapshots."""

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class Controls:
    left: int
    right: int
    jump: int
    shoot: int


PLAYER_CONTROLS = (
    Controls(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w, shoot=pygame.K_s),
    Controls(
        left=pygame.K_LEFT,
        right=pygame.K_RIGHT,
        jump=pygame.K_UP,
        shoot=pygame.K_DOWN,
    ),
)


class InputState:
    __slots__ = ("left", "right", "jump", "shoot_down", "shoot_pressed", "shoot_released")

    def __init__(self):
        self.left = False
        self.right = False
        self.jump = False
        self.shoot_down = False
        self.shoot_pressed = False
        self.shoot_released = False


def read_input(keys, controls, was_shoot_down):
    """Build one player's input state for this frame.

    Returns ``(state, shoot_down)`` so the caller can remember the previous
    state and detect press/release edges next frame.
    """
    state = InputState()
    state.left = bool(keys[controls.left])
    state.right = bool(keys[controls.right])
    state.jump = bool(keys[controls.jump])

    down = bool(keys[controls.shoot])
    state.shoot_down = down
    state.shoot_pressed = down and not was_shoot_down
    state.shoot_released = was_shoot_down and not down
    return state, down
