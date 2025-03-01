import pygame
import random
import time
import json
import os
import pygame.mixer

# Fixed key for encryption and decryption
key = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
values = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210'
encryption_dict = dict(zip(key, values))
decryption_dict = dict(zip(values, key))


def encrypt(data):
    return ''.join(encryption_dict.get(char, char) for char in data)


def decrypt(data):
    return ''.join(decryption_dict.get(char, char) for char in data)


pygame.init()
pygame.mixer.init()

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
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
PURPLE = (128, 0, 128)
DARK_BLUE = (25, 25, 112)
TEAL = (0, 128, 128)
PINK = (255, 192, 203)
GOLD = (255, 215, 0)
SKY_BLUE = (135, 206, 235)
NAVY = (0, 0, 128)

# Killer Settings
KILLER_SPEED = 5
TOP_KILLER_WIDTH = 30
TOP_KILLER_HEIGHT = 50
SIDE_KILLER_WIDTH = 50
SIDE_KILLER_HEIGHT = 25
SPAWN_INTERVAL = 1200  # Milliseconds between spawns

# Difficulty Settings
Spawn_Rate = 10  # How many Milliseconds should go down from Spawn Delay after every difficulty increase
Difficulty_Increase = 0.5  # Increase in Killer Speed
Difficulty_Threshold = 3  # How many points per difficulty increase
TOKEN_REWARD_INTERVAL = 45  # Every 45 score gives 1 token

# Screen Properties
WIDTH = 1250
HEIGHT = 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge Game")
clock = pygame.time.Clock()

# Player Settings
PLAYER_BODY_WIDTH = 50
PLAYER_BODY_HEIGHT = 70
PLAYER_HEAD_RADIUS = 20
CROUCHHEIGHT = 30  # Height of the player when crouching
CROUCH_OFFSET = 70  # Offset for crouching position
PLAYERX = 200
PLAYERY = HEIGHT - PLAYER_BODY_HEIGHT - PLAYER_HEAD_RADIUS + 50
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
Tokens = 0
previous_token_milestone = 0
token_reward_accumulated = 0
current_round_tokens = 0

# Game state
killers = []
last_spawn_time = 0
game_state = "menu"  # "menu", "game", "shop", "game_over", "settings", "code_entry", "developer"
dev_mode = False

# Shop background colors
shop_background_colors = [
    PURPLE,
    DARK_BLUE,
    TEAL,
    NAVY,
    SKY_BLUE
]
current_shop_bg = 0

# Player Skins
player_skins = [
    {"body": RED, "head": ORANGE, "name": "Default", "unlocked": True},
    {"body": BLUE, "head": SKY_BLUE, "name": "Blue", "unlocked": False},
    {"body": GREEN, "head": LIME, "name": "Green", "unlocked": False},
    {"body": PURPLE, "head": PINK, "name": "Purple", "unlocked": False},
    {"body": BLACK, "head": DARK_GRAY, "name": "Shadow", "unlocked": False}
]
current_skin = 0

# Active Power-ups
active_powerups = {
    "Double Points": {"active": False, "time_left": 0},
    "Extra Life": {"active": False, "count": 0},
    "Slow Motion": {"active": False, "time_left": 0}
}

# Settings
settings = {
    "volume": 0.8,  # 0.0 to 1.0
    "keybinds": {
        "double_points": pygame.K_1,
        "extra_life": pygame.K_2,
        "slow_motion": pygame.K_3
    }
}




# Sound effects
try:
    jump_sound = pygame.mixer.Sound("sounds/jump.wav")
    death_sound = pygame.mixer.Sound("sounds/death.wav")
    point_sound = pygame.mixer.Sound("sounds/point.wav")
    powerup_sound = pygame.mixer.Sound("sounds/powerup.wav")
    button_sound = pygame.mixer.Sound("sounds/button.wav")
except:
    # Create dummy sounds if files not found
    jump_sound = pygame.mixer.Sound(buffer=bytearray([]))
    death_sound = pygame.mixer.Sound(buffer=bytearray([]))
    point_sound = pygame.mixer.Sound(buffer=bytearray([]))
    powerup_sound = pygame.mixer.Sound(buffer=bytearray([]))
    button_sound = pygame.mixer.Sound(buffer=bytearray([]))

# Set default volume
jump_sound.set_volume(settings["volume"])
death_sound.set_volume(settings["volume"])
point_sound.set_volume(settings["volume"])
powerup_sound.set_volume(settings["volume"])
button_sound.set_volume(settings["volume"])

# Code entry variables
code_input = ""
code_message = ""
code_message_timer = 0


# Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)  # Border

        font = pygame.font.SysFont("comicsans", 30)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.rect.collidepoint(mouse_pos) and mouse_clicked


# Create buttons
play_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 60, "Play", GREEN, LIME)
shop_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 60, "Shop", ORANGE, YELLOW)
settings_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 110, 200, 60, "Settings", BLUE, SKY_BLUE, WHITE)
back_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 60, "Back", GRAY, WHITE)
restart_button = Button(WIDTH // 2 - 210, HEIGHT // 2 + 80, 200, 60, "Restart", GREEN, LIME)
quit_button = Button(WIDTH // 2 + 10, HEIGHT // 2 + 80, 200, 60, "Quit", RED, ORANGE)
change_bg_button = Button(WIDTH - 220, HEIGHT - 100, 200, 60, "Change Theme", SKY_BLUE, BLUE, WHITE)
codes_button = Button(WIDTH - 220, HEIGHT - 170, 200, 60, "Enter Code", GOLD, YELLOW)
submit_code_button = Button(WIDTH // 2 + 10, HEIGHT // 2 + 90, 200, 60, "Submit", GREEN, LIME)
cancel_code_button = Button(WIDTH // 2 - 210, HEIGHT // 2 + 90, 200, 60, "Cancel", RED, ORANGE)

dev_save_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 60, "Save & Exit", GREEN, LIME)
token_add_button = Button(WIDTH // 2 + 100, HEIGHT // 2 - 200, 80, 40, "+100", GREEN, LIME)
token_sub_button = Button(WIDTH // 2 + 190, HEIGHT // 2 - 200, 80, 40, "-100", RED, ORANGE)
hs_add_button = Button(WIDTH // 2 + 100, HEIGHT // 2 - 140, 80, 40, "+100", GREEN, LIME)
hs_sub_button = Button(WIDTH // 2 + 190, HEIGHT // 2 - 140, 80, 40, "-100", RED, ORANGE)
unlock_all_button = Button(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 60, "Unlock All Abilities", BLUE, SKY_BLUE, WHITE)
reset_data_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 30, 300, 60, "Reset Game Data", RED, ORANGE, WHITE)

shop_items = [
    {"name": "Double Points", "cost": 5, "description": "Double score for 30 seconds (one-time use)", "purchased": False, "used": False},
    {"name": "Extra Life", "cost": 10, "description": "Survive one hit with the revive button", "purchased": False, "used": False},
    {"name": "Slow Motion", "cost": 15, "description": "Slow down killers for 15 seconds (one-time use)", "purchased": False, "used": False},
    {"name": "Player Skin", "cost": 20, "description": "Change player color", "purchased": False, "used": False}
]





# UI Functions
def draw_menu():
    screen.fill(BLUE)

    # Title
    title_font = pygame.font.SysFont("comicsans", 60)
    title = title_font.render("DODGE GAME", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    # Stats
    stats_font = pygame.font.SysFont("comicsans", 30)
    highscore_text = stats_font.render(f"Highscore: {HighScore}", True, WHITE)
    tokens_text = stats_font.render(f"Tokens: {Tokens}", True, YELLOW)
    screen.blit(highscore_text, (WIDTH // 2 - highscore_text.get_width() // 2, 180))
    screen.blit(tokens_text, (WIDTH // 2 - tokens_text.get_width() // 2, 220))

    # Buttons
    play_button.draw()
    shop_button.draw()
    settings_button.draw()
    codes_button.draw()

    # Draw player character using current skin
    draw_player(WIDTH // 2 - 25, HEIGHT - 200, False, False)

    pygame.display.flip()


# Modified apply_code function with developer mode
def apply_code(code):
    global Tokens, code_message, valid_codes, game_state, dev_mode

    code = code.strip().upper()

    # Special code for developer menu
    if code == "DEVMODE":
        dev_mode = True
        game_state = "developer"
        code_message = "Developer mode activated."
        return True

    # Normal code processing
    if code in valid_codes:
        if not valid_codes[code]["used"]:
            Tokens += valid_codes[code]["tokens"]
            valid_codes[code]["used"] = True
            code_message = f"Success! You received {valid_codes[code]['tokens']} tokens."
            save_game_data()
            return True
        else:
            code_message = "This code has already been used."
    else:
        code_message = f"Invalid code: '{code}'. Please try again."

    return False



# Function to draw the developer menu
def draw_developer_menu():
    screen.fill(DARK_BLUE)

    # Title
    title_font = pygame.font.SysFont("comicsans", 50)
    title = title_font.render("DEVELOPER MENU", True, RED)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    # Token display
    dev_font = pygame.font.SysFont("comicsans", 30)
    token_text = dev_font.render(f"Current Tokens: {Tokens}", True, GOLD)
    screen.blit(token_text, (WIDTH // 2 - 200, HEIGHT // 2 - 200))

    # Highscore display
    hs_text = dev_font.render(f"Current Highscore: {HighScore}", True, LIME)
    screen.blit(hs_text, (WIDTH // 2 - 200, HEIGHT // 2 - 140))

    # Ability status
    ability_text = dev_font.render("Abilities Status:", True, WHITE)
    screen.blit(ability_text, (WIDTH // 2 - 200, HEIGHT // 2 - 80))

    # Draw buttons
    token_add_button.draw()
    token_sub_button.draw()
    hs_add_button.draw()
    hs_sub_button.draw()
    unlock_all_button.draw()
    reset_data_button.draw()
    dev_save_button.draw()

    # Show abilities
    ability_y = HEIGHT // 2 + 100
    for item in shop_items:
        if item["name"] != "Player Skin":
            status = "Purchased" if item["purchased"] and not item["used"] else (
                "Used" if item["purchased"] and item["used"] else "Not Purchased")
            status_color = GREEN if status == "Purchased" else (ORANGE if status == "Used" else RED)

            ability_status = dev_font.render(f"{item['name']}: {status}", True, status_color)
            screen.blit(ability_status, (WIDTH // 2 - 200, ability_y))
            ability_y += 40

    pygame.display.flip()


def reset_game():
    global PLAYERX, PLAYERY, JUMPING_SPEED, is_jumping, is_crouching, killers, last_spawn_time, Score, NewHS
    global KILLER_SPEED, SPAWN_INTERVAL, previous_token_milestone, token_reward_accumulated, current_round_tokens
    global active_powerups, Tokens  # Make sure Tokens is included here

    # Now you can use Tokens
    if Tokens < 0:
        Tokens = 0

    PLAYERX = 200
    Score = 0
    NewHS = False
    PLAYERY = HEIGHT - PLAYER_BODY_HEIGHT - PLAYER_HEAD_RADIUS
    JUMPING_SPEED = 0
    is_jumping = False
    is_crouching = False
    killers = []
    last_spawn_time = 0
    KILLER_SPEED = 5
    SPAWN_INTERVAL = 1200
    previous_token_milestone = 0
    token_reward_accumulated = 0
    current_round_tokens = 0

    # Reset all powerups
    active_powerups = {
        "Double Points": {"active": False, "time_left": 0},
        "Extra Life": {"active": False, "count": 0},
        "Slow Motion": {"active": False, "time_left": 0}
    }


# Function to unlock all abilities
def unlock_all_abilities():
    global shop_items

    for item in shop_items:
        item["purchased"] = True
        item["used"] = False

    # Unlock all skins
    for skin in player_skins:
        skin["unlocked"] = True

    save_game_data()


# Add the developer menu handling to the main game loop
def handle_developer_menu(mouse_pos, mouse_clicked):
    global Tokens, HighScore, game_state

    token_add_button.check_hover(mouse_pos)
    token_sub_button.check_hover(mouse_pos)
    hs_add_button.check_hover(mouse_pos)
    hs_sub_button.check_hover(mouse_pos)
    unlock_all_button.check_hover(mouse_pos)
    reset_data_button.check_hover(mouse_pos)
    dev_save_button.check_hover(mouse_pos)

    if token_add_button.is_clicked(mouse_pos, mouse_clicked):
        Tokens += 100
        button_sound.play()

    elif token_sub_button.is_clicked(mouse_pos, mouse_clicked):
        Tokens = max(0, Tokens - 100)  # Don't go below 0
        button_sound.play()

    elif hs_add_button.is_clicked(mouse_pos, mouse_clicked):
        HighScore += 100
        button_sound.play()

    elif hs_sub_button.is_clicked(mouse_pos, mouse_clicked):
        HighScore = max(0, HighScore - 100)  # Don't go below 0
        button_sound.play()

    elif unlock_all_button.is_clicked(mouse_pos, mouse_clicked):
        unlock_all_abilities()
        button_sound.play()

    elif reset_data_button.is_clicked(mouse_pos, mouse_clicked):
        reset_game_data()
        button_sound.play()

    elif dev_save_button.is_clicked(mouse_pos, mouse_clicked):
        save_game_data()
        button_sound.play()
        game_state = "menu"  # Return to main menu


def draw_settings():
    screen.fill(DARK_BLUE)

    # Title
    title_font = pygame.font.SysFont("comicsans", 50)
    title = title_font.render("SETTINGS", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    # Volume slider
    volume_font = pygame.font.SysFont("comicsans", 30)
    volume_text = volume_font.render(f"Game Volume: {int(settings['volume'] * 100)}%", True, WHITE)
    screen.blit(volume_text, (WIDTH // 2 - 200, 150))

    # Draw volume slider background
    pygame.draw.rect(screen, DARK_GRAY, (WIDTH // 2 - 200, 190, 400, 20), border_radius=10)

    # Draw volume slider fill
    pygame.draw.rect(screen, GREEN,
                     (WIDTH // 2 - 200, 190, int(400 * settings["volume"]), 20),
                     border_radius=10)

    # Draw slider knob
    knob_pos = (WIDTH // 2 - 200) + int(400 * settings["volume"])
    pygame.draw.circle(screen, WHITE, (knob_pos, 200), 15)
    pygame.draw.circle(screen, BLACK, (knob_pos, 200), 15, 2)

    # Keybind settings
    keybind_title = volume_font.render("Ability Keybinds:", True, WHITE)
    screen.blit(keybind_title, (WIDTH // 2 - 200, 250))

    # Keybind buttons
    ability_y = 300
    for ability, key in settings["keybinds"].items():
        ability_name = ability.replace("_", " ").title()
        key_name = pygame.key.name(key).upper()

        ability_text = volume_font.render(f"{ability_name}:", True, WHITE)
        screen.blit(ability_text, (WIDTH // 2 - 200, ability_y))

        # Draw key button
        key_rect = pygame.Rect(WIDTH // 2 + 50, ability_y, 100, 40)
        pygame.draw.rect(screen, GRAY, key_rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, key_rect, 2, border_radius=5)

        key_text = volume_font.render(key_name, True, BLACK)
        screen.blit(key_text, (key_rect.x + key_rect.width // 2 - key_text.get_width() // 2,
                               key_rect.y + key_rect.height // 2 - key_text.get_height() // 2))

        ability_y += 60

    # Back button
    back_button.draw()

    pygame.display.flip()


def draw_code_entry():
    screen.fill(DARK_BLUE)

    # Title
    title_font = pygame.font.SysFont("comicsans", 50)
    title = title_font.render("ENTER CODE", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    # Code input box
    code_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 50, 400, 60)
    pygame.draw.rect(screen, WHITE, code_rect, border_radius=5)
    pygame.draw.rect(screen, BLACK, code_rect, 2, border_radius=5)

    # Display entered code
    code_font = pygame.font.SysFont("comicsans", 30)
    code_text = code_font.render(code_input, True, BLACK)
    screen.blit(code_text, (code_rect.x + 10, code_rect.y + code_rect.height // 2 - code_text.get_height() // 2))

    # Show blinking cursor
    if pygame.time.get_ticks() % 1000 < 500 and len(code_input) < 20:
        cursor_x = code_rect.x + 10 + code_text.get_width()
        pygame.draw.line(screen, BLACK, (cursor_x, code_rect.y + 15), (cursor_x, code_rect.y + code_rect.height - 15),
                         2)

    # Instructions
    instructions_font = pygame.font.SysFont("comicsans", 25)
    instructions = instructions_font.render("Enter a valid code to receive tokens", True, WHITE)
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, code_rect.y - 40))

    # Message (if any)
    if code_message:
        message_color = GREEN if "Success" in code_message else RED
        message_text = instructions_font.render(code_message, True, message_color)
        screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, code_rect.y + 80))

    # Buttons
    submit_code_button.draw()
    cancel_code_button.draw()

    pygame.display.flip()


def initialize_codes():
    global valid_codes

    # Define default codes if they don't exist 1234
    if not hasattr(globals(), 'valid_codes') or valid_codes is None:
        valid_codes = {
            "LAUNCH2025": {"tokens": 10, "used": False},
            "DODGEPRO": {"tokens": 15, "used": False},
            "CUBEMASTER": {"tokens": 20, "used": False},
            "DEVCODE": {"tokens": 50, "used": False},
            "RELEASE": {"tokens": 5, "used": False},
            "ALTREI": {"tokens": -1, "used": False}
        }

    # Make sure all codes have the 'used' property
    for code, data in valid_codes.items():
        if "used" not in data:
            data["used"] = False

# Update the draw_shop function to reflect one-time use abilities
def draw_shop():
    # Use the current shop background color
    screen.fill(shop_background_colors[current_shop_bg])

    # Title
    title_font = pygame.font.SysFont("comicsans", 50)
    title = title_font.render("SHOP", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    # Tokens display
    tokens_font = pygame.font.SysFont("comicsans", 30)
    tokens_text = tokens_font.render(f"Tokens: {Tokens}", True, GOLD)
    screen.blit(tokens_text, (WIDTH // 2 - tokens_text.get_width() // 2, 110))

    # Shop items
    item_font = pygame.font.SysFont("comicsans", 25)
    y_offset = 180

    for i, item in enumerate(shop_items):
        item_rect = pygame.Rect(WIDTH // 2 - 200, y_offset, 400, 80)
        pygame.draw.rect(screen, DARK_GRAY, item_rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, item_rect, 2, border_radius=5)

        name_text = item_font.render(item["name"], True, WHITE)
        desc_text = item_font.render(item["description"], True, GRAY)

        # Special handling based on item status
        if item["purchased"] and not item["used"]:
            if item["name"] == "Player Skin":
                status_text = item_font.render("Select Skin", True, GREEN)
                screen.blit(status_text,
                            (item_rect.x + item_rect.width - status_text.get_width() - 10, item_rect.y + 10))
            else:
                status_text = item_font.render("Ready to Use", True, GREEN)
                screen.blit(status_text,
                            (item_rect.x + item_rect.width - status_text.get_width() - 10, item_rect.y + 10))

                # If this is a usable ability, show the keybind
                if item["name"] in ["Double Points", "Slow Motion"]:
                    ability_key = "1" if item["name"] == "Double Points" else "3"
                    keybind_text = item_font.render(f"Use: [{ability_key}]", True, YELLOW)
                    screen.blit(keybind_text,
                                (item_rect.x + item_rect.width - keybind_text.get_width() - 10, item_rect.y + 40))
        elif item["purchased"] and item["used"] and item["name"] != "Player Skin":
            status_text = item_font.render("Used", True, RED)
            screen.blit(status_text, (item_rect.x + item_rect.width - status_text.get_width() - 10, item_rect.y + 10))

            # Show buy again option
            buy_rect = pygame.Rect(item_rect.x + item_rect.width - 150, item_rect.y + 40, 140, 30)
            pygame.draw.rect(screen, GREEN if Tokens >= item["cost"] else DARK_GRAY, buy_rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, buy_rect, 2, border_radius=5)

            buy_text = item_font.render("Buy Again", True, WHITE)
            screen.blit(buy_text, (buy_rect.x + buy_rect.width // 2 - buy_text.get_width() // 2,
                                   buy_rect.y + buy_rect.height // 2 - buy_text.get_height() // 2))
        elif not item["purchased"]:
            cost_text = item_font.render(f"{item['cost']} Tokens", True, GOLD)
            screen.blit(cost_text, (item_rect.x + item_rect.width - cost_text.get_width() - 10, item_rect.y + 10))

        screen.blit(name_text, (item_rect.x + 10, item_rect.y + 10))
        screen.blit(desc_text, (item_rect.x + 10, item_rect.y + 40))

        # Buy button (only show if not purchased or if used and can be purchased again)
        if not item["purchased"] or (item["used"] and item["name"] != "Player Skin"):
            buy_rect = pygame.Rect(item_rect.x + item_rect.width - (150 if item["used"] else 80),
                                   item_rect.y + 40,
                                   140 if item["used"] else 70, 30)

            # We've already drawn this for used items above, so only draw for not purchased items
            if not item["used"]:
                pygame.draw.rect(screen, GREEN if Tokens >= item["cost"] else DARK_GRAY, buy_rect, border_radius=5)
                pygame.draw.rect(screen, BLACK, buy_rect, 2, border_radius=5)

                buy_text = item_font.render("Buy", True, WHITE)
                screen.blit(buy_text, (buy_rect.x + buy_rect.width // 2 - buy_text.get_width() // 2,
                                       buy_rect.y + buy_rect.height // 2 - buy_text.get_height() // 2))

        # Show skin selector if player skin was purchased
        if item["name"] == "Player Skin" and item["purchased"]:
            skin_button_width = 70
            button_gap = 10
            total_width = (skin_button_width + button_gap) * len(player_skins)
            start_x = item_rect.x + (item_rect.width - total_width) // 2

            for j, skin in enumerate(player_skins):
                skin_button_color = skin["body"] if skin["unlocked"] else DARK_GRAY
                skin_button = pygame.Rect(start_x + j * (skin_button_width + button_gap),
                                          item_rect.y + 40,
                                          skin_button_width, 30)
                pygame.draw.rect(screen, skin_button_color, skin_button, border_radius=5)
                pygame.draw.rect(screen, BLACK, skin_button, 2, border_radius=5)

                # Highlight current selected skin
                if j == current_skin and skin["unlocked"]:
                    pygame.draw.rect(screen, WHITE, skin_button, 3, border_radius=5)

        y_offset += 100

    # Back button and change background button
    back_button.draw()
    change_bg_button.draw()

    pygame.display.flip()


def draw_player(x, y, is_crouching, is_jumping):
    current_skin_data = player_skins[current_skin]

    # Draw body (rectangle)
    body_height = PLAYER_BODY_HEIGHT if not is_crouching else CROUCHHEIGHT
    body_y = y + (PLAYER_BODY_HEIGHT - body_height) if is_crouching else y

    # Draw body first (behind the head)
    body_rect = pygame.Rect(x, body_y, PLAYER_BODY_WIDTH, body_height)
    pygame.draw.rect(screen, current_skin_data["body"], body_rect)
    pygame.draw.rect(screen, BLACK, body_rect, 2)  # Add border

    # Draw head (circle) on top of body
    head_y = body_y - PLAYER_HEAD_RADIUS  # Position head above body
    pygame.draw.circle(screen, current_skin_data["head"], (x + PLAYER_BODY_WIDTH // 2, head_y), PLAYER_HEAD_RADIUS)
    pygame.draw.circle(screen, BLACK, (x + PLAYER_BODY_WIDTH // 2, head_y), PLAYER_HEAD_RADIUS, 2)  # Add border

    # Draw eyes
    eye_radius = 4
    eye_offset = 7
    pygame.draw.circle(screen, WHITE, (x + PLAYER_BODY_WIDTH // 2 - eye_offset, head_y - 2), eye_radius)
    pygame.draw.circle(screen, WHITE, (x + PLAYER_BODY_WIDTH // 2 + eye_offset, head_y - 2), eye_radius)
    pygame.draw.circle(screen, BLACK, (x + PLAYER_BODY_WIDTH // 2 - eye_offset, head_y - 2), 2)  # pupils
    pygame.draw.circle(screen, BLACK, (x + PLAYER_BODY_WIDTH // 2 + eye_offset, head_y - 2), 2)  # pupils

    # Draw simple smile
    pygame.draw.arc(screen, BLACK,
                    (x + PLAYER_BODY_WIDTH // 2 - 10, head_y, 20, 15),
                    0, 3.14, 2)

    return (body_rect, pygame.Rect(x + PLAYER_BODY_WIDTH // 2 - PLAYER_HEAD_RADIUS,
                                   head_y - PLAYER_HEAD_RADIUS,
                                   PLAYER_HEAD_RADIUS * 2, PLAYER_HEAD_RADIUS * 2))


def draw_game_screen():
    screen.fill(YELLOW)

    # Calculate player position for drawing
    player_y = PLAYERY
    body, head = draw_player(PLAYERX, player_y, is_crouching, is_jumping)

    # Draw killers
    for killer in killers:
        pygame.draw.rect(screen, BROWN, killer)
    # Draw UI
    font = pygame.font.SysFont("comicsans", 30)
    text2 = font.render("Score: " + str(Score), True, BLACK)
    text3 = font.render("HighScore: " + str(HighScore), True, BLACK)
    tokens_text = font.render(f"Tokens: {Tokens}", True, ORANGE)
    token_progress = font.render(f"Next token: {Score % TOKEN_REWARD_INTERVAL}/{TOKEN_REWARD_INTERVAL}", True, ORANGE)

    screen.blit(text2, (10, 10))
    screen.blit(text3, (WIDTH - 250, 10))
    screen.blit(tokens_text, (WIDTH - 250, 50))
    screen.blit(token_progress, (WIDTH - 300, 90))

    # Draw active powerups
    powerup_y = 150
    for powerup, data in active_powerups.items():
        if (powerup == "Double Points" and data["active"]) or \
                (powerup == "Extra Life" and data["count"] > 0) or \
                (powerup == "Slow Motion" and data["active"]):

            if powerup == "Extra Life":
                powerup_text = font.render(f"{powerup}: {data['count']} remaining", True, GREEN)
            else:
                powerup_text = font.render(f"{powerup}: {data['time_left'] // 1000}s", True, GREEN)

            screen.blit(powerup_text, (WIDTH - 300, powerup_y))
            powerup_y += 40

    pygame.display.flip()

revive_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 160, 200, 60, "Revive", GREEN, LIME)

def draw_game_over():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 50)
    text = font.render("Game Over!", True, RED)
    text2 = font.render(f"Highscore: {HighScore}", True, LIME)
    text3 = font.render(f"Score: {Score}", True, LIME)
    tokens_text = font.render(f"Tokens: {Tokens}", True, YELLOW)

    tokens_earned_text = font.render(f"Tokens earned this round: +{current_round_tokens}", True, GOLD)

    # Split out the token rewards for clarity
    tokens_from_score = Score // TOKEN_REWARD_INTERVAL
    tokens_detail = font.render(f"From score: +{tokens_from_score}", True, ORANGE)

    # Show highscore bonus separately
    highscore_bonus = ""
    if NewHS and HighScore > 0:
        highscore_bonus = font.render("New Highscore Bonus: +2", True, BLUE)

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 220))
    screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 - 160))
    screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 - 110))
    screen.blit(tokens_text, (WIDTH // 2 - tokens_text.get_width() // 2, HEIGHT // 2 - 60))

    screen.blit(tokens_earned_text, (WIDTH // 2 - tokens_earned_text.get_width() // 2, HEIGHT // 2 - 10))
    screen.blit(tokens_detail, (WIDTH // 2 - tokens_detail.get_width() // 2, HEIGHT // 2 + 30))

    if NewHS and HighScore > 0:
        screen.blit(highscore_bonus, (WIDTH // 2 - highscore_bonus.get_width() // 2, HEIGHT // 2 + 230))

    # Regular buttons
    restart_button.draw()
    quit_button.draw()

    # Check if Extra Life is available (purchased but not used)
    extra_life_available = False
    for item in shop_items:
        if item["name"] == "Extra Life" and item["purchased"] and not item["used"]:
            extra_life_available = True
            break

    # Draw revive button if Extra Life is available
    if extra_life_available:
        revive_button.draw()

    pygame.display.flip()


# Update the shop button logic in the main loop
def handle_shop_buttons(mouse_pos, mouse_clicked):
    global Tokens, current_skin

    y_offset = 180
    for i, item in enumerate(shop_items):
        item_rect = pygame.Rect(WIDTH // 2 - 200, y_offset, 400, 80)

        # Define buy button rect based on whether item is used or not
        if not item["purchased"] or (item["used"] and item["name"] != "Player Skin"):
            buy_rect = pygame.Rect(item_rect.x + item_rect.width - (150 if item["used"] else 80),
                                   item_rect.y + 40,
                                   140 if item["used"] else 70, 30)

            if buy_rect.collidepoint(mouse_pos) and mouse_clicked:
                if Tokens >= item["cost"]:
                    button_sound.play()
                    Tokens -= item["cost"]
                    item["purchased"] = True
                    item["used"] = False  # Reset used status

                    save_game_data()

        # Check skin selection if Player Skin is purchased
        if item["name"] == "Player Skin" and item["purchased"]:
            skin_button_width = 70
            button_gap = 10
            total_width = (skin_button_width + button_gap) * len(player_skins)
            start_x = item_rect.x + (item_rect.width - total_width) // 2

            for j, skin in enumerate(player_skins):
                skin_button = pygame.Rect(start_x + j * (skin_button_width + button_gap),
                                          item_rect.y + 40,
                                          skin_button_width, 30)

                if skin_button.collidepoint(mouse_pos) and mouse_clicked and skin["unlocked"]:
                    button_sound.play()
                    current_skin = j
                    save_game_data()

        y_offset += 100


def initialize_shop_items():
    global shop_items

    # Make sure every shop item has a 'used' property
    for item in shop_items:
        if "used" not in item:
            item["used"] = False

def update_powerups(time_delta):
    global KILLER_SPEED, active_powerups

    # Update Double Points timer
    if active_powerups["Double Points"]["active"]:
        active_powerups["Double Points"]["time_left"] -= time_delta
        if active_powerups["Double Points"]["time_left"] <= 0:
            active_powerups["Double Points"]["active"] = False

    # Update Slow Motion timer
    if active_powerups["Slow Motion"]["active"]:
        active_powerups["Slow Motion"]["time_left"] -= time_delta
        if active_powerups["Slow Motion"]["time_left"] <= 0:
            active_powerups["Slow Motion"]["active"] = False
            # Restore normal speed
            KILLER_SPEED = KILLER_SPEED * 2


def reset_game_data():
    global HighScore, Tokens, shop_items, current_shop_bg, current_skin, player_skins, valid_codes

    HighScore = 0
    Tokens = 0
    current_shop_bg = 0
    current_skin = 0

    # Reset shop items
    for item in shop_items:
        item["purchased"] = False
        item["used"] = False

    # Reset player skins
    for i, skin in enumerate(player_skins):
        if i == 0:  # Default skin
            skin["unlocked"] = True
        else:
            skin["unlocked"] = False

    # Reset valid codes
    for code in valid_codes:
        valid_codes[code]["used"] = False

    save_game_data()


def save_game_data():
    game_data = {
        'HighScore': HighScore,
        'Tokens': Tokens,
        'ShopItems': shop_items,
        'ShopBackground': current_shop_bg,
        'Settings': settings,
        'ValidCodes': valid_codes,
        'CurrentSkin': current_skin,
        'PlayerSkins': player_skins
    }

    filename = 'gamedata.json'
    encrypted_data = encrypt(json.dumps(game_data))
    with open(filename, 'w') as file:
        file.write(encrypted_data)
    print(f"Game data saved: HS={HighScore}, Tokens={Tokens}")


def load_game_data():
    global HighScore, Tokens, shop_items, current_shop_bg, settings, valid_codes, current_skin, player_skins
    filename = 'gamedata.json'
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            encrypted_data = file.read()
            try:
                decrypted_data = decrypt(encrypted_data)
                data = json.loads(decrypted_data)
                HighScore = data['HighScore']
                Tokens = data['Tokens']
                if 'ShopItems' in data:
                    shop_items = data['ShopItems']
                if 'ShopBackground' in data:
                    current_shop_bg = data['ShopBackground']
                if 'Settings' in data:
                    settings = data['Settings']
                if 'ValidCodes' in data:
                    valid_codes = data['ValidCodes']
                if 'CurrentSkin' in data:
                    current_skin = data['CurrentSkin']
                if 'PlayerSkins' in data:
                    player_skins = data['PlayerSkins']
                print(f"Game data loaded: HS={HighScore}, Tokens={Tokens}")
            except json.JSONDecodeError:
                print("Error decoding JSON data. Game data will be reset.")
                HighScore = 0
                Tokens = 0
    else:
        print("Game data file does not exist. Starting with new game data.")


def check_player_collision(body_rect, head_rect, killer_rect):
    """Check if either the player's body or head collides with a killer"""
    return body_rect.colliderect(killer_rect) or head_rect.colliderect(killer_rect)


def activate_powerup(powerup_name):
    global KILLER_SPEED

    # Only activate if player has purchased this powerup and it's not used
    item_available = False
    for item in shop_items:
        if item["name"] == powerup_name and item["purchased"] and not item["used"]:
            item_available = True
            break

    if not item_available:
        return False

    if powerup_name == "Double Points":
        active_powerups["Double Points"]["active"] = True
        active_powerups["Double Points"]["time_left"] = 30000  # 30 seconds

        # Mark as used
        for item in shop_items:
            if item["name"] == "Double Points":
                item["used"] = True
                break

        powerup_sound.play()
        return True

    elif powerup_name == "Slow Motion":
        active_powerups["Slow Motion"]["active"] = True
        active_powerups["Slow Motion"]["time_left"] = 15000  # 15 seconds
        # Cut killer speed in half
        KILLER_SPEED = KILLER_SPEED / 2

        # Mark as used
        for item in shop_items:
            if item["name"] == "Slow Motion":
                item["used"] = True
                break

        powerup_sound.play()
        return True

    return False


# Main game loop
def main():
    global game_state, PLAYERX, PLAYERY, is_jumping, is_crouching, JUMPING_SPEED
    global Score, HighScore, NewHS, Tokens, previous_token_milestone, token_reward_accumulated, current_round_tokens
    global KILLER_SPEED, SPAWN_INTERVAL, killers, last_spawn_time, current_shop_bg, settings, current_skin
    global code_input, code_message, code_message_timer
    global player_skins, active_powerups

    run = True

    load_game_data()
    initialize_shop_items()
    initialize_codes()

    while run:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        current_time = pygame.time.get_ticks()
        frame_time = clock.get_time()  # Time since last frame in milliseconds

        if Tokens < 0:
            Tokens = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game_data()
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True

            # Handle text input for code entry
            elif event.type == pygame.KEYDOWN:
                if game_state == "code_entry":
                    if event.key == pygame.K_RETURN:
                        apply_code(code_input)
                        code_message_timer = current_time
                    elif event.key == pygame.K_BACKSPACE:
                        code_input = code_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "menu"
                    else:
                        # Only allow reasonable characters for codes
                        if event.unicode.isalnum() and len(code_input) < 20:
                            code_input += event.unicode

                # Ability activation
                if game_state == "game":
                    if event.key == settings["keybinds"]["double_points"]:
                        activate_powerup("Double Points")
                    elif event.key == settings["keybinds"]["slow_motion"]:
                        activate_powerup("Slow Motion")

        if game_state == "menu":
            play_button.check_hover(mouse_pos)
            shop_button.check_hover(mouse_pos)
            settings_button.check_hover(mouse_pos)
            codes_button.check_hover(mouse_pos)

            if play_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                game_state = "game"
                reset_game()

            elif shop_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                game_state = "shop"

            elif settings_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                game_state = "settings"

            elif codes_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                game_state = "code_entry"
                code_input = ""
                code_message = ""

            draw_menu()

        # MOVED THIS HERE - Developer menu should be at the same level as other game states
        elif game_state == "developer":
            handle_developer_menu(mouse_pos, mouse_clicked)
            draw_developer_menu()

        elif game_state == "settings":
            back_button.check_hover(mouse_pos)

            if back_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                game_state = "menu"
                save_game_data()

            # Volume slider interaction
            slider_rect = pygame.Rect(WIDTH // 2 - 200, 190, 400, 20)
            if pygame.mouse.get_pressed()[0] and slider_rect.collidepoint(mouse_pos):
                # Calculate volume based on x position
                x_pos = mouse_pos[0]
                new_volume = (x_pos - (WIDTH // 2 - 200)) / 400
                settings["volume"] = max(0, min(1, new_volume))

                # Update sound volumes
                jump_sound.set_volume(settings["volume"])
                death_sound.set_volume(settings["volume"])
                point_sound.set_volume(settings["volume"])
                powerup_sound.set_volume(settings["volume"])
                button_sound.set_volume(settings["volume"])

                save_game_data()

            # Keybind button interaction
            ability_y = 300
            for ability, key in list(settings["keybinds"].items()):  # Create a copy of items to iterate
                key_rect = pygame.Rect(WIDTH // 2 + 50, ability_y, 100, 40)

                if key_rect.collidepoint(mouse_pos) and mouse_clicked:
                    # Start listening for a new key
                    waiting_for_key = True
                    current_ability = ability

                    # Wait for a key press
                    while waiting_for_key:
                        for ev in pygame.event.get():
                            if ev.type == pygame.KEYDOWN:
                                settings["keybinds"][current_ability] = ev.key
                                waiting_for_key = False
                                save_game_data()
                                break
                            elif ev.type == pygame.MOUSEBUTTONDOWN:
                                waiting_for_key = False
                                break

                        # Redraw to show "Press a key" message
                        draw_settings()
                        pygame.display.flip()

                ability_y += 60

            draw_settings()

        elif game_state == "code_entry":
            submit_code_button.check_hover(mouse_pos)
            cancel_code_button.check_hover(mouse_pos)

            if submit_code_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                apply_code(code_input)
                code_message_timer = current_time

            elif cancel_code_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                game_state = "menu"

            # Handle code message timeout
            if code_message and current_time - code_message_timer > 3000:  # 3 seconds timeout
                code_message = ""

            draw_code_entry()

        elif game_state == "shop":
            back_button.check_hover(mouse_pos)
            change_bg_button.check_hover(mouse_pos)

            if back_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                game_state = "menu"
                save_game_data()

            if change_bg_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                current_shop_bg = (current_shop_bg + 1) % len(shop_background_colors)
                save_game_data()

            # Handle shop item interactions using the updated function
            handle_shop_buttons(mouse_pos, mouse_clicked)

            draw_shop()

        elif game_state == "game":
            body_height = PLAYER_BODY_HEIGHT if not is_crouching else CROUCHHEIGHT
            body_y = PLAYERY + (PLAYER_BODY_HEIGHT - body_height) if is_crouching else PLAYERY
            head_y = body_y - PLAYER_HEAD_RADIUS

            player_body = pygame.Rect(PLAYERX, body_y, PLAYER_BODY_WIDTH, body_height)
            player_head = pygame.Rect(PLAYERX + PLAYER_BODY_WIDTH // 2 - PLAYER_HEAD_RADIUS,
                                      head_y - PLAYER_HEAD_RADIUS,
                                      PLAYER_HEAD_RADIUS * 2,
                                      PLAYER_HEAD_RADIUS * 2)

            # Update powerups
            update_powerups(frame_time)

            keys = pygame.key.get_pressed()

            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and PLAYERX > 0:
                PLAYERX -= SPEED
            if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and PLAYERX + PLAYER_BODY_WIDTH < WIDTH:
                PLAYERX += SPEED
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[
                pygame.K_w]) and PLAYERY == HEIGHT - PLAYER_BODY_HEIGHT - PLAYER_HEAD_RADIUS and not is_jumping:
                JUMPING_SPEED = -JUMPING_STRENGTH
                is_jumping = True
                jump_sound.play()

            if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not is_jumping:
                is_crouching = True
            else:
                is_crouching = False

            if is_jumping:
                PLAYERY += JUMPING_SPEED
                JUMPING_SPEED += GRAVITY
                if PLAYERY >= HEIGHT - PLAYER_BODY_HEIGHT - PLAYER_HEAD_RADIUS:
                    PLAYERY = HEIGHT - PLAYER_BODY_HEIGHT - PLAYER_HEAD_RADIUS
                    JUMPING_SPEED = 0
                    is_jumping = False

            if keys[pygame.K_ESCAPE]:
                game_state = "menu"
                save_game_data()

            if current_time - last_spawn_time > SPAWN_INTERVAL:
                spawn_side = random.choice(['top', 'right'])
                if spawn_side == 'top':
                    spawn_x = random.randint(0, WIDTH - TOP_KILLER_WIDTH)
                    killers.append(pygame.Rect(spawn_x, -TOP_KILLER_HEIGHT, TOP_KILLER_WIDTH, TOP_KILLER_HEIGHT))
                else:
                    spawn_y = random.randint(40, 150)
                    killers.append(pygame.Rect(WIDTH, HEIGHT - spawn_y, SIDE_KILLER_WIDTH, SIDE_KILLER_HEIGHT))
                last_spawn_time = current_time

            for killer in killers[:]:
                if killer.width == TOP_KILLER_WIDTH:
                    killer.y += KILLER_SPEED
                    if killer.y > HEIGHT:
                        killers.remove(killer)

                        # Apply Double Points if active
                        points = 2 if active_powerups["Double Points"]["active"] else 1
                        Score += points
                        point_sound.play()

                        # Calculate tokens earned from score
                        token_reward_accumulated = Score // TOKEN_REWARD_INTERVAL
                        current_round_tokens = token_reward_accumulated

                        if Score > HighScore:
                            HighScore = Score
                            NewHS = True
                            if Tokens < 0:
                                Tokens = 0

                        if Score % Difficulty_Threshold == 0:
                            KILLER_SPEED += Difficulty_Increase - 0.25
                            SPAWN_INTERVAL -= Spawn_Rate
                else:
                    killer.x -= KILLER_SPEED
                    if killer.x < -SIDE_KILLER_WIDTH:
                        killers.remove(killer)

                        # Apply Double Points if active
                        points = 2 if active_powerups["Double Points"]["active"] else 1
                        Score += points
                        point_sound.play()

                        # Calculate tokens earned from score
                        token_reward_accumulated = Score // TOKEN_REWARD_INTERVAL
                        current_round_tokens = token_reward_accumulated

                        if Score > HighScore:
                            HighScore = Score
                            NewHS = True
                            if Tokens < 0:
                                Tokens = 0

                        if Score % Difficulty_Threshold == 0:
                            KILLER_SPEED += Difficulty_Increase - 0.25
                            SPAWN_INTERVAL -= Spawn_Rate
                            if Tokens < 0:
                                Tokens = 0

            # Check collisions
            collision_occurred = False
            for killer in killers:
                if check_player_collision(player_body, player_head, killer):
                    collision_occurred = True

                    # Add token rewards at the end of the game
                    token_rewards = Score // TOKEN_REWARD_INTERVAL

                    # Add bonus tokens for new highscore (only if it's not the first time)
                    if NewHS and HighScore > 0:
                        token_rewards += 2

                    Tokens += token_rewards
                    current_round_tokens = token_rewards

                    death_sound.play()
                    game_state = "game_over"
                    save_game_data()
                    break

            draw_game_screen()

        elif game_state == "game_over":
            restart_button.check_hover(mouse_pos)
            quit_button.check_hover(mouse_pos)

            # Check for Extra Life availability
            extra_life_available = False
            for item in shop_items:
                if item["name"] == "Extra Life" and item["purchased"] and not item["used"]:
                    extra_life_available = True
                    revive_button.check_hover(mouse_pos)

                    if revive_button.is_clicked(mouse_pos, mouse_clicked):
                        button_sound.play()

                        # Mark Extra Life as used
                        item["used"] = True
                        save_game_data()

                        # Revive player at the same position but clear all killers
                        killers.clear()

                        # Reset spawn timer to give player a chance
                        last_spawn_time = current_time

                        # Return to the game
                        game_state = "game"
                        powerup_sound.play()
                        break

            if restart_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                reset_game()
                game_state = "game"

            elif quit_button.is_clicked(mouse_pos, mouse_clicked):
                button_sound.play()
                game_state = "menu"

            draw_game_over()

    pygame.quit()


if __name__ == "__main__":
    main()
