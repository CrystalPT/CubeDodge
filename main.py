import pygame
import random
import time
import json
import os

# Simple substitution cipher for "encryption"
def encrypt(data):
    encrypted = []
    key = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    values = ''.join(random.sample(key, len(key)))
    encryption_dict = dict(zip(key, values))
    for char in data:
        encrypted.append(encryption_dict.get(char, char))
    return ''.join(encrypted)

# Decrypt function for reading the data back
def decrypt(data):
    decrypted = []
    key = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    values = ''.join(random.sample(key, len(key)))
    decryption_dict = dict(zip(values, key))
    for char in data:
        decrypted.append(decryption_dict.get(char, char))
    return ''.join(decrypted)

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
LIME = (0, 200, 20)
BROWN = (139, 69, 19)

# Killer Settings
KILLER_SPEED = 5
TOP_KILLER_WIDTH = 30
TOP_KILLER_HEIGHT = 50
SIDE_KILLER_WIDTH = 50
SIDE_KILLER_HEIGHT = 25
SPAWN_INTERVAL = 1200  # Milliseconds between spawns

Spawn_Rate = 10  # How many Milliseconds should go down from Spawn Delay after every difficulty increase
Difficulty_Increase = 0.5  # Increase in Killer Speed
Difficulty_Threshold = 3  # How many points per difficulty increase

# Screen Properties
WIDTH = 1100
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cube Game - CrystalPT")
clock = pygame.time.Clock()

# Player Settings
PLAYERWIDTH = 50
PLAYERHEIGHT = 90
CROUCHHEIGHT = 40  # Height of the player when crouching
CROUCH_OFFSET = 50  # Offset for crouching position
PLAYERX = 200
PLAYERY = HEIGHT - PLAYERHEIGHT
SPEED = 8
JUMPING_STRENGTH = 10
JUMPING_SPEED = 0
GRAVITY = 0.5
is_jumping = False
is_crouching = False

# Score
Score = 0
HighScore = 0
NewHS = False

# Killer Management
killers = []
last_spawn_time = 0

def draw(player, killers):
    screen.fill(YELLOW)
    pygame.draw.rect(screen, RED, player)
    font = pygame.font.SysFont("comicsans", 30)
    text2 = font.render("Score: " + str(Score), True, BLACK)
    text3 = font.render("HighScore: " + str(HighScore), True, BLACK)
    coords = font.render(f"Coordinates: X:{PLAYERWIDTH / 2 + PLAYERX}, Y:{PLAYERY + 90}", True, RED)
    screen.blit(text2, (10, 10))
    screen.blit(text3, (WIDTH - 250, 10))
    screen.blit(coords, (WIDTH - 750, 10))
    for killer in killers:
        pygame.draw.rect(screen, BROWN, killer)
    pygame.display.flip()

def draw_game_over():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 50)
    text = font.render(f"Game Over! Press R to Restart or Q to Quit.", True, RED)
    text2 = font.render(f"HighScore: {HighScore}", True, LIME)
    text3 = font.render(f"Score: {Score}", True, LIME)
    newhs = font.render("NEW HIGHSCORE!", True, BLUE)
    if NewHS:
        screen.blit(newhs, (WIDTH // 2 - 170, HEIGHT // 2 - text.get_height() // 2 + 120))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    screen.blit(text2, (WIDTH // 2 - 120, HEIGHT // 2 - text.get_height() // 2 + 80))
    screen.blit(text3, (WIDTH // 2 - 80, HEIGHT // 2 - text.get_height() // 2 + 40))
    pygame.display.flip()

def reset_game():
    global PLAYERX, PLAYERY, JUMPING_SPEED, is_jumping, is_crouching, killers, last_spawn_time
    PLAYERX = 200
    Score = 0
    NewHS = False
    PLAYERY = HEIGHT - PLAYERHEIGHT
    JUMPING_SPEED = 0
    is_jumping = False
    is_crouching = False
    killers = []
    last_spawn_time = 0

def save_high_score():
    filename = 'highscore.json'
    encrypted_data = encrypt(json.dumps({'HighScore': HighScore}))
    with open(filename, 'w') as file:
        file.write(encrypted_data)

def load_high_score():
    global HighScore
    filename = 'highscore.json'
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            encrypted_data = file.read()
            decrypted_data = decrypt(encrypted_data)
            data = json.loads(decrypted_data)
            HighScore = data['HighScore']

game_over = False
run = True

load_high_score()  # Load the high score at the start

while run:
    clock.tick(60)

    if not game_over:
        player_height = PLAYERHEIGHT if not is_crouching else CROUCHHEIGHT
        player_y = PLAYERY + CROUCH_OFFSET if is_crouching else PLAYERY
        player = pygame.Rect(PLAYERX, player_y, PLAYERWIDTH, player_height)

        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score()
                run = False
                break

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and PLAYERX > 0:
            PLAYERX -= SPEED
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and PLAYERX + PLAYERWIDTH < WIDTH:
            PLAYERX += SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and PLAYERY == HEIGHT - PLAYERHEIGHT and not is_jumping:
            JUMPING_SPEED = -JUMPING_STRENGTH
            is_jumping = True

        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not is_jumping:
            is_crouching = True
        else:
            is_crouching = False

        if is_jumping:
            PLAYERY += JUMPING_SPEED
            JUMPING_SPEED += GRAVITY
            if PLAYERY >= HEIGHT - PLAYERHEIGHT:
                PLAYERY = HEIGHT - PLAYERHEIGHT
                JUMPING_SPEED = 0
                is_jumping = False

        if current_time - last_spawn_time > SPAWN_INTERVAL:
            spawn_side = random.choice(['top', 'right'])
            if spawn_side == 'top':
                spawn_x = random.randint(0, WIDTH - TOP_KILLER_WIDTH)
                killers.append(pygame.Rect(spawn_x, -TOP_KILLER_HEIGHT, TOP_KILLER_WIDTH, TOP_KILLER_HEIGHT))
            else:
                spawn_y = random.randint(10, 90)
                killers.append(pygame.Rect(WIDTH, HEIGHT - spawn_y, SIDE_KILLER_WIDTH, SIDE_KILLER_HEIGHT))
            last_spawn_time = current_time

        for killer in killers[:]:
            if killer.width == TOP_KILLER_WIDTH:
                killer.y += KILLER_SPEED
                if killer.y > HEIGHT:
                    killers.remove(killer)
                    Score += 1
                    if Score > HighScore:
                        HighScore = Score
                        NewHS = True
                    if Score % Difficulty_Increase == 0:
                        KILLER_SPEED += Difficulty_Increase - 0.25
                        SPAWN_INTERVAL -= Spawn_Rate
            else:
                killer.x -= KILLER_SPEED
                if killer.x < -SIDE_KILLER_WIDTH:
                    killers.remove(killer)
                    Score += 1
                    if Score > HighScore:
                        HighScore = Score
                        NewHS = True
                    if Score % Difficulty_Increase == 0:
                        KILLER_SPEED += Difficulty_Increase - 0.25
                        SPAWN_INTERVAL -= Spawn_Rate

        for killer in killers:
            if player.colliderect(killer):
                game_over = True

        draw(player, killers)
    else:
        draw_game_over()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    Score = 0
                    Spawn_Rate = 0
                    KILLER_SPEED = 5
                    NewHS = False
                    game_over = False
                elif event.key == pygame.K_q:
                    save_high_score()
                    run = False

pygame.quit()
