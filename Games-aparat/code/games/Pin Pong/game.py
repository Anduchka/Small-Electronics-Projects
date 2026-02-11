import random

PATH = "games/Pin Pong/"

top_border = 30
bottom_border = 98

left_border = 4
right_border = 123

ball_x, ball_y = 64, 76
ball_dir_x, ball_dir_y = 0, 0

player_y = 60
player_dir = 0

bot_y = 60

score_p = 0
score_b = 0

start = False

def move_player(move_dir):
    global player_y
    
    if move_dir == 1 and player_y + 10 < bottom_border:
        player_y += move_dir
    elif move_dir == -1 and player_y > top_border + 1:
        player_y += move_dir

def move_bot():
    global bot_y
    
    if ball_dir_x != 1:
        return 
    
    d_border = 20
    move_dir = 0
    
    if bot_y + 5 > ball_y:
        move_dir = -1
    elif bot_y + 5 < ball_y:
        move_dir = 1
    
    r = random.random()
    
    if r > 0.95:
        move_dir *= -1
    elif r < 0.05:
        move_dir = 0
    
    if ball_x > 100:
        d_border = 0
    
    if move_dir == 1 and bot_y + 10 < bottom_border - d_border:
        bot_y += move_dir
    elif move_dir == -1 and bot_y > top_border + 1 + d_border:
        bot_y += move_dir

def reset_ball():
    global ball_x, ball_y, ball_dir_x, ball_dir_y
    
    ball_x, ball_y = 64, 76
        
    ball_dir_x = random.choice([1, -1])
    ball_dir_y = random.choice([1, -1])

def move_ball(api):
    global ball_x, ball_y, score_p, score_b, ball_dir_x, ball_dir_y
    
    ball_x += ball_dir_x
    ball_y += ball_dir_y
    
    if ball_y <= top_border + 1 or ball_y >= bottom_border - 2:
        ball_dir_y *= -1
        api["play_wav"](PATH + "bounce.wav")
    
    if (ball_x <= left_border + 1 and ball_x > left_border and ball_y in range(player_y - 1, player_y + 11)) or (ball_x >= right_border - 1 and ball_x < right_border and ball_y in range(bot_y - 1, bot_y + 11)):
        ball_dir_x *= -1
        api["play_wav"](PATH + "bounce.wav")
        if random.random() > 0.7:
            ball_dir_y *= -1

    if ball_x <= 0:
        score_b += 1
        reset_ball()
        api["play_wav"]("loose.wav")
    if ball_x >= 127:
        score_p += 1
        reset_ball()
        api["play_wav"]("win.wav")

def run(api):
    global start, player_dir
    
    if not api["in_bar"]:
    
        if api["ok"][0] == "released":
            if not start:
                reset_ball()
                start = True
    
        if start:
            if api["up"][0] == "pressed" or api["up"][0] == "down":
                player_dir = -1
            elif api["down"][0] == "pressed" or api["down"][0] == "down":
                player_dir = 1
            else:
                player_dir = 0
    
        move_player(player_dir)
        move_bot()
        move_ball(api)
        move_ball(api)
    
    t_sc_p = f"{score_p:<3}"
    t_sc_b = f"{score_b:>3}"
    
    api["display"].text(t_sc_p, 40, top_border + 2, 1)
    api["display"].text(t_sc_b, 65, top_border + 2, 1)
    
    api["display"].rect(ball_x - 1, ball_y - 1, 4, 4, 0)
    api["display"].rect(ball_x, ball_y, 2, 2, 1)
    
    api["display"].rect(left_border, player_y, 2, 10, 1)
    api["display"].rect(right_border, bot_y, 2, 10, 1)
    
    api["display"].hline(0, top_border, 128, 1)
    api["display"].hline(0, bottom_border, 128, 1)
    
    return True
    