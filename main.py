"""Entry point for Hoops 1v1."""

import pygame

from constants import TITLE, WINDOW_HEIGHT, WINDOW_WIDTH
from game import Game


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    Game(screen).run()
    pygame.quit()


if __name__ == "__main__":
    main()
