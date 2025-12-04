import pygame

TILE = 48


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.vx = 1.6
        self.patrol_min = x - 2 * TILE
        self.patrol_max = x + 2 * TILE

    def update(self):
        self.rect.x += self.vx
        if self.rect.x < self.patrol_min or self.rect.x > self.patrol_max:
            self.vx *= -1
