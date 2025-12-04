import sys
import players
import coin
import enemy
import pygame
import platform

pygame.init()

# ============================
#       CONFIGURACIÓN
# ============================
WIDTH, HEIGHT = 900, 540
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer - 3 Niveles")
CLOCK = pygame.time.Clock()
FPS = 60

# Colores
SKY = (135, 206, 235)
GROUND = (100, 60, 20)
PLAYER_COLOR = (50, 120, 255)
ENEMY_COLOR = (200, 50, 50)
PLATFORM_COLOR = (100, 200, 100)
COIN_COLOR = (255, 200, 0)
TEXT_COLOR = (30, 30, 30)

# Fuentes
FONT = pygame.font.SysFont("Arial", 22)
FONT_BIG = pygame.font.SysFont("Arial", 48)
FONT_MED = pygame.font.SysFont("Arial", 38)
TILE = 48

# ============================
#       VARIABLES GLOBALES
# ============================
life_lost_msg_time = 0
level_complete_msg_time = 0
level_index = 0
platforms = []
coins = []
enemies = []
player = None
goal_rect = None
camera_x = 0
score = 0
lives = 3
game_over = False
all_levels_completed = False

# ============================
#       NIVELES
# ============================
LEVELS = [
    [
        "................................................................................",
        "..........C.....................................C.............................",
        "....................#####.....................................................",
        ".......................................#####......E...........................",
        "...........#####...............................#####..........................",
        "P.....................C.........E..######.....................................",
        "##########...........#########..............######............................",
        "................................................................................",
        "..............#####...................................C.......................",
        ".................................................#####.......................",
        "###############################...........############################.G.#####",
    ],
    [
        "................................................................................",
        "................C..........................................C....................",
        ".................#####.........................................................",
        "........................E............##########................................",
        "..........#####............######..E...............#########....................",
        "P....................C.........E........######..................................",
        "##########...........#########...................######........................",
        "..............#####...C.........................................................",
        "................................................................E..............",
        ".................................#####...........#####.........................",
        "###############################...........############################.G.#####",
    ],
    [
        "................................................................................",
        "......C......................C.................................................",
        ".......................#####..................................................",
        ".....................E...............#####.....................................",
        "..........#####................................#####............................",
        "P....................C........E..######....E...................................",
        "#########..............#########..............######..........................",
        "..............########...........................................C..............",
        "............................................................................",
        ".........................#####......................E.........................",
        "###############################...........############################.G.#####",
    ]
]


# ============================
#       NIVELES / RESTART
# ============================
def load_level(index):
    global platforms, coins, enemies, player, goal_rect, camera_x
    platforms = []
    coins = []
    enemies = []
    goal_rect = None
    camera_x = 0

    LEVEL_MAP = LEVELS[index]

    for row_i, row in enumerate(LEVEL_MAP):
        for col_i, ch in enumerate(row):
            x = col_i * TILE
            y = row_i * TILE
            if ch == '#':
                platforms.append(platform.Platform(x, y, TILE, TILE))
            elif ch == 'C':
                coins.append(coin.Coin(x + TILE // 4, y + TILE // 4))
            elif ch == 'E':
                enemies.append(enemy.Enemy(x, y))
            elif ch == 'P':
                global player
                player = players.Players(x, y)
            elif ch == 'G':
                goal_rect = pygame.Rect(x, y, TILE, TILE)
    return player


def restart():
    global score, lives, game_over, all_levels_completed, level_index
    score = 0
    lives = 3
    game_over = False
    all_levels_completed = False
    level_index = 0
    load_level(level_index)


# ============================
#       LÓGICA DEL JUEGO
# ============================
def game_logic(keys):
    global score, lives, game_over, level_index, all_levels_completed, camera_x, life_lost_msg_time, level_complete_msg_time

    if game_over or all_levels_completed:
        return

    # Salto
    if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and player.on_ground:
        player.vy = -player.jump_power

    # Movimiento
    player.update(keys, platforms)

    # Limitar dentro de la pantalla
    if player.rect.x < camera_x:
        player.rect.x = camera_x
    if player.rect.right > camera_x + WIDTH:
        player.rect.right = camera_x + WIDTH

    # Cámara
    camera_x = player.rect.centerx - WIDTH // 2
    if camera_x < 0:
        camera_x = 0

    # Caída
    if player.rect.top > HEIGHT + 200:
        lives -= 1
        life_lost_msg_time = pygame.time.get_ticks()
        if lives <= 0:
            game_over = True
        else:
            load_level(level_index)

    # Monedas
    for coin in coins[:]:
        if player.rect.colliderect(coin):
            coins.remove(coin)
            score += 10

    # Enemigos
    for e in enemies[:]:
        e.update()
        if player.rect.colliderect(e.rect):
            if player.vy > 0:  # saltando sobre enemigo
                enemies.remove(e)
                player.vy = -10
                score += 20
            else:  # golpeado por enemigo
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    load_level(level_index)

    # Meta
    if goal_rect and player.rect.colliderect(goal_rect):
        level_complete_msg_time = pygame.time.get_ticks()
        level_index += 1
        if level_index >= len(LEVELS):
            all_levels_completed = True
        else:
            load_level(level_index)


# ============================
#       DIBUJO
# ============================
def draw():
    SCREEN.fill(SKY)

    # Plataformas
    for plat in platforms:
        r = pygame.Rect(plat.x - camera_x, plat.y, plat.width, plat.height)
        pygame.draw.rect(SCREEN, PLATFORM_COLOR, r)
        pygame.draw.rect(SCREEN, GROUND, (r.x, r.y + r.height // 2, r.width, r.height // 2))

    # Monedas
    for coin in coins:
        r = pygame.Rect(coin.x - camera_x, coin.y, coin.width, coin.height)
        pygame.draw.ellipse(SCREEN, COIN_COLOR, r)

    # Enemigos
    for e in enemies:
        r = pygame.Rect(e.rect.x - camera_x, e.rect.y, e.rect.width, e.rect.height)
        pygame.draw.rect(SCREEN, ENEMY_COLOR, r)

    # Meta
    if goal_rect:
        r = pygame.Rect(goal_rect.x - camera_x, goal_rect.y, goal_rect.width, goal_rect.height)
        pygame.draw.rect(SCREEN, (255, 215, 0), r)

    # Jugador
    pr = pygame.Rect(player.rect.x - camera_x, player.rect.y, player.rect.width, player.rect.height)
    pygame.draw.rect(SCREEN, PLAYER_COLOR, pr)

    # HUD
    hud = FONT.render(f"Puntos: {score}   Vidas: {lives}   Nivel: {level_index + 1}/3", True, TEXT_COLOR)
    SCREEN.blit(hud, (10, 10))

    current_time = pygame.time.get_ticks()

    if game_over:
        msgOne = FONT_BIG.render("¡GAME OVER!", True, (255, 40, 40))
        msgTwo = FONT_MED.render("Oprime R para reiniciar", True, (255, 40, 40))
        SCREEN.blit(msgOne, (WIDTH // 2 - msgOne.get_width() // 2, HEIGHT // 2 - msgOne.get_height() // 2))
        SCREEN.blit(msgTwo, (WIDTH // 2 - msgTwo.get_width() // 2, HEIGHT // 2 + 20))

    if all_levels_completed:
        msgOne = FONT_BIG.render("¡GANASTE EL JUEGO!", True, (50, 200, 50))
        msg2 = FONT.render("Presiona R para reiniciar", True, TEXT_COLOR)
        SCREEN.blit(msgOne, (WIDTH // 2 - msgOne.get_width() // 2, HEIGHT // 2 - 50))
        SCREEN.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 + 20))

    if current_time - life_lost_msg_time < 1200 and life_lost_msg_time != 0:
        msg = FONT_BIG.render("¡Perdiste una vida!", True, (255, 80, 80))
        SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 4))

    if current_time - level_complete_msg_time < 1000 and level_complete_msg_time != 0:
        msg = FONT_BIG.render("¡Nivel Completado!", True, (50, 200, 50))
        SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 4))

    pygame.display.flip()


# ============================
#       INICIO DEL JUEGO
# ============================
player = load_level(0)


def main():
    running = True
    while running:
        CLOCK.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                restart()

        game_logic(keys)
        draw()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
