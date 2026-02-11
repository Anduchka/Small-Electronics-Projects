import random

PATH = "games/Defender/"
audio = None

player_x, player_y = 64, 116

wave = 1
kills = 0
player_bullets = 10
start = False

shoot_speed = 50
spawn_delay = 100
spawn_timer = 0
move_delay = 5
move_timer = 0

enemies_state = []
enemies_reload = []
enemies_x = []
enemies_y = []

spawn_quota_max = 5
spawn_quota = 5
max_spawn = 3

bullets_dir = []
bullets_x = []
bullets_y = []

def make_bullet(x, y, d=1):
    audio(PATH + "laser.wav")
    bullets_x.append(x)
    bullets_y.append(y)
    
    bullets_dir.append(d)

def make_enemy():
    global enemies_x, enemies_y, enemies_reload, enemies_state, spawn_quota
    
    if spawn_quota == 0:
        return
    
    count = random.randint(1, max_spawn)
    
    while spawn_quota - count < 0:
        if enemies_state and len(enemies_state) == 0:
            count = random.randint(1, max_spawn)
        else:
            count = random.randint(0, max_spawn)
    
    existing = []
    
    for i in range(count):
        r_x = random.randint(10, 117)
        collision = 1
        attempts = 0
        
        while collision > 0:
            collision = 0
            attempts += 1
            
            if attempts > 30:
                break
            
            for e_x in existing:
                if r_x in range(e_x - 5, e_x + 6):
                    collision += 1
                    r_x = random.randint(10, 117)
                    break
        
        existing.append(r_x)
        enemies_y.append(15)
        enemies_x.append(r_x)
        enemies_reload.append(shoot_speed)
        enemies_state.append(1)
    
    spawn_quota -= count

def move_enemies():
    global move_timer, enemies_x, enemies_y, enemies_reload, enemies_state
    
    move_timer -= 1
    
    if move_timer <= 0:
        move_timer = move_delay
        
        to_remove = set()
        
        for i, e in enumerate(enemies_state):
            if e == 0:
                enemies_state[i] = -1
                continue
            elif e == -1:
                to_remove.add(i)
                continue
            
            enemies_y[i] += 1
         
        new_enemies_state = []
        new_enemies_reload = []
        new_enemies_x = []
        new_enemies_y = []
    
        for i in range(len(enemies_state)):
            if i not in to_remove:
                new_enemies_state.append(enemies_state[i])
                new_enemies_reload.append(enemies_reload[i])
                new_enemies_x.append(enemies_x[i])
                new_enemies_y.append(enemies_y[i])
    
        enemies_state = new_enemies_state
        enemies_reload = new_enemies_reload
        enemies_x = new_enemies_x
        enemies_y = new_enemies_y
         
    for i, e in enumerate(enemies_reload):
        if enemies_state[i] == 0:
            continue
        if e <= 0:
            enemies_reload[i] = shoot_speed + random.randint(-10, 10)
            make_bullet(enemies_x[i], enemies_y[i] + 1, 1)
        else:
            enemies_reload[i] -= 1

def enemy_collision(i):
    global enemies_state, kills, player_bullets
    
    if bullets_dir[i] == 1:
        return -1
    
    for o, e in enumerate(enemies_state):
        if e != 1:
            continue
            
        if bullets_y[i] in range(enemies_y[o] - 4, enemies_y[o] - 1):
            if bullets_x[i] in range(enemies_x[o] - 3, enemies_x[o] + 4):
                enemies_state[o] = 0
                kills += 1
                audio(PATH + "explosion.wav")
                player_bullets += 2
                return i
    
    return -1

def ground_collision(i):
    global player_bullets
    
    if bullets_y[i] in range(player_y - 3, player_y):
        if bullets_x[i] in range(player_x - 2, player_x + 3):
            if player_bullets > 0:
                player_bullets = 1
            else:
                player_bullets = 0
            audio(PATH + "hurt.wav")
            return i
    
    elif bullets_y[i] > player_y:
        return i
    
    return -1

def out_check(i):
    if bullets_y[i] > player_y + 1 or bullets_y[i] < 12:
        return True
    
    return False

def move_bullets():
    global bullets_x, bullets_y, bullets_dir
    
    to_remove = set()
    
    for i, d in enumerate(bullets_dir):
        bullets_y[i] += d * 2
        
        if d == -1:
            c = enemy_collision(i)
        else:
            c = ground_collision(i)
        
        if c != -1:
            to_remove.add(c)
        elif out_check(i):
            to_remove.add(i)
    
    new_bullets_dir = []
    new_bullets_x = []
    new_bullets_y = []
    
    for i in range(len(bullets_dir)):
        if i not in to_remove:
            new_bullets_dir.append(bullets_dir[i])
            new_bullets_x.append(bullets_x[i])
            new_bullets_y.append(bullets_y[i])
    
    bullets_dir = new_bullets_dir
    bullets_x = new_bullets_x
    bullets_y = new_bullets_y

def enemies_win_check():
    global wave, start, kills, player_bullets, shoot_speed, spawn_delay, spawn_timer, move_delay, move_timer, enemies_state, max_spawn
    global enemies_reload, enemies_x, enemies_y, spawn_quota_max, spawn_quota, bullets_dir, bullets_x, bullets_y, player_y, player_x
    
    for y in enemies_y:
        if y > player_y:
            audio("loose.wav")
            start = False
            
            player_x, player_y = 64, 116

            wave = 1
            kills = 0
            player_bullets = 10

            shoot_speed = 50
            spawn_delay = 100
            spawn_timer = 0
            move_delay = 5
            move_timer = 0

            enemies_state = []
            enemies_reload = []
            enemies_x = []
            enemies_y = []

            spawn_quota_max = 5
            spawn_quota = 5
            max_spawn = 3

            bullets_dir = []
            bullets_x = []
            bullets_y = []

def draw_enemies(api):
    for i in range(len(enemies_state)):
        x, y = enemies_x[i], enemies_y[i]
        if enemies_state[i] == 1:
            api["display"].hline(x - 1, y - 3, 3, 1)
            api["display"].hline(x - 3, y - 2, 7, 1)
            api["display"].hline(x - 1, y - 1, 3, 1)
            api["display"].pixel(x, y, 1)
            api["display"].pixel(x - 3, y - 1, 1)
            api["display"].pixel(x + 3, y - 1, 1)
        else:
            api["display"].line(x - 2, y - 3, x + 2, y, 1)
            api["display"].line(x - 2, y, x + 2, y - 3, 1)
            api["display"].pixel(x - 2, y - 3, 1)
            api["display"].pixel(x + 1, y + 1, 1)
            api["display"].pixel(x + 4, y - 3, 1)
            api["display"].pixel(x - 3, y + 2, 1)
            
def draw_bullets(api):
    for i in range(len(bullets_dir)):
        api["display"].pixel(bullets_x[i], bullets_y[i], 1)

def draw_player(api):
    api["display"].hline(player_x - 2, player_y, 5, 1)
    api["display"].hline(player_x - 2, player_y - 1, 5, 1)
    
    api["display"].pixel(player_x - 1, player_y - 2, 1)
    api["display"].pixel(player_x + 1, player_y - 2, 1)

def draw_ui(api):
    api["display"].hline(0, player_y + 1, 128, 1)
    api["display"].text("Ammo:" + str(player_bullets), 2, player_y + 3, 1)
    api["display"].text("##" + str(player_bullets), 137, player_y + 3, 1)
    
    wave_text = "V" + str(wave)
    wave_text = f"{wave_text:>5}"
    api["display"].text(wave_text, 80, player_y + 3, 1)

def init(api):
    global audio
    audio = api["play_wav"]

def run(api):
    global player_x, spawn_timer, spawn_quota, wave, spawn_quota_max, start, player_bullets, shoot_speed, spawn_delay, move_delay, max_spawn
    
    if not api["in_bar"]:
        
        if not start and api["ok"][0] == "released":
            start = True
    
        if start:
            
            if api["left"][0] == "pressed" or api["left"][0] == "down":
                player_x += 1
            elif api["right"][0] == "pressed" or api["right"][0] == "down":
                player_x -= 1
            
            player_x = max(2, min(125, player_x))
            
            if api["ok"][0] == "pressed" and player_bullets > 0:
                make_bullet(player_x, player_y - 3, -1)
                player_bullets -= 1
            
            move_enemies()
            move_bullets()
            enemies_win_check()
            
            if spawn_timer <= 0:
                make_enemy()
                spawn_timer = spawn_delay
            else:
                spawn_timer -= 1
            
            if spawn_quota <= 0 and len(enemies_state) == 0:
                wave += 1
                spawn_quota_max += 1
                spawn_quota = spawn_quota_max
                
                audio("win.wav")
                
                if wave % 3 == 0:
                    shoot_speed -= 7
                    spawn_delay -= 1
                if wave % 5 == 0:
                    move_delay -= 1
                    max_spawn += 3
                    
                    max_spawn = min(10, max_spawn)
                      
    draw_enemies(api)
    draw_bullets(api)
    draw_player(api)
    draw_ui(api)        
    
    return True
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    