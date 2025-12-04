import pygame

TILE = 48


class Coin(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, TILE // 2, TILE // 2)
