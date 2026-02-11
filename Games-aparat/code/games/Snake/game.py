import random

PATH = "games/Snake/"

margin = 5
cell_size = 3
field_w = 128 - margin
field_h = 116 - margin
cells_w = field_w // cell_size
cells_h = field_h // cell_size

player_speed = 1
player_x, player_y = 20, 19
player_dir = -1
player_tail = []

dead = False
restart_timer = 0
restart_messgage = ""

apple_x, apple_y = -1, -1

def offset_to_screen(x, y):
    n_x = x * cell_size
    n_y = y * cell_size
    
    n_x = n_x + margin - 1
    n_y = n_y + 12 + margin - 1
    
    return n_x, n_y

def new_apple():
    global apple_x, apple_y
    
    if len(player_tail) + 1 >=  cells_w * cells_h:
        apple_x = apple_y = -1
        return
    
    proper = False
    n_x = random.randint(2, cells_w - 3)
    n_y = random.randint(2, cells_h - 3)
    
    while not proper:
        proper = True
    
        for x, y in player_tail:
            if n_x == x and n_y == y:
                proper = False
                n_x = random.randint(2, cells_w - 3)
                n_y = random.randint(2, cells_h - 3)
                break
            
    apple_x, apple_y = n_x, n_y

def move_snake(api):
    global player_x, player_y, dead, player_speed
    
    if len(player_tail) >= 1:
        for i in range(len(player_tail) - 1, 0, -1):
            player_tail[i] = player_tail[i - 1].copy()
        
        player_tail[0] = [player_x, player_y]
    
    if player_dir == 0:
        player_y -= player_speed
    elif player_dir == 1:
        player_x -= player_speed
    elif player_dir == 2:
        player_y += player_speed
    elif player_dir == 3:
        player_x += player_speed
    
    if player_x == apple_x and player_y == apple_y:
        api["play_wav"](PATH + "apple.wav")
        new_apple()
        player_tail.append([-1, -1])
    
    if player_x <= 0 or player_y <= 0 or player_x >= cells_w - 2 or player_y >= cells_h - 2:
        dead = True
    for x, y in player_tail:
        if player_x == x and player_y == y:
            dead = True

def init(api):
    if apple_x == -1 or apple_y == -1:
        new_apple()

def run(api):
    global apple_x, apple_y, player_x, player_y, player_dir, player_tail, dead, restart_timer, restart_messgage
    
    if dead:
        api["play_wav"]("loose.wav")
        new_apple()
        player_x, player_y = 20, 19
        player_dir = -1
        player_tail = []
        restart_messgage = "You Lost"
        restart_timer = 30
        dead = False
    
    if len(player_tail) > 100:
        api["play_wav"](PATH + "win.wav")
        new_apple()
        player_x, player_y = 20, 19
        player_dir = -1
        player_tail = []
        restart_messgage = "You Won!"
        restart_timer = 30
        dead = False
    
    if restart_timer > 0:
        restart_timer -=1
        api["display"].text(restart_messgage, 36, 50, 1)
        return True
    
    if api["up"][0] == "pressed" and player_dir != 2:
        player_dir = 0
    elif api["right"][0] == "pressed" and player_dir != 3:
        player_dir = 1
    elif api["down"][0] == "pressed" and player_dir != 0:
        player_dir = 2
    elif api["left"][0] == "pressed" and player_dir != 1:
        player_dir = 3
        
    if not api["in_bar"]:
        move_snake(api)
    
    api["display"].rect(margin, margin + 12, 118, 106, 1)
    
    ax, ay = offset_to_screen(apple_x, apple_y)
    api["display"].rect(ax, ay, cell_size, cell_size, 1)
    
    px, py = offset_to_screen(player_x, player_y)
    api["display"].fill_rect(px, py, cell_size, cell_size, 1)
    
    for x, y in player_tail:
        if x == -1 or y == -1:
            continue 
        tx, ty = offset_to_screen(x, y)
        api["display"].rect(tx, ty, cell_size, cell_size, 1)
    
    return True
    