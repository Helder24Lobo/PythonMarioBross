import pygame

TILE = 48


class Players:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.speed = 5
        self.jump_power = 13

    def update(self, keys, platforms):
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed

        self.vy += 0.7
        if self.vy > 18:
            self.vy = 18

        self.rect.x += self.vx
        self.collide(self.vx, 0, platforms)
        self.rect.y += int(self.vy)
        self.on_ground = False
        self.collide(0, self.vy, platforms)

    def collide(self, vx, vy, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat):
                if vx > 0:
                    self.rect.right = plat.left
                if vx < 0:
                    self.rect.left = plat.right
                if vy > 0:
                    self.rect.bottom = plat.top
                    self.vy = 0
                    self.on_ground = True
                if vy < 0:
                    self.rect.top = plat.bottom
                    self.vy = 0
