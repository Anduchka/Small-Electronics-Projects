import random

PATH = "games/Black Jack/"

all_card_pol = []

player_card_pol = []
player_score = 0
player_score_alt = 0
p_won = False
bet = 10
total = 1000

bot_card_pol = []
bot_score = 0
bot_score_alt = 0
b_won = False
move_delay = 0

turn = -1
selected = 0

buttons_count = 3

def card_value(c):
    if c in ["X", "J", "Q", "K"]:
        return 10
    elif c == "A":
        return 1
    
    return c

def create_pol():
    new_card_pol = []
    
    total_value = 0
    
    while total_value < 50:
        num = random.choice([2, 3, 4, 5, 6, 7, 8, 9, "X", "J", "Q", "K", "A"])
        tip = random.randint(0, 3)
        
        exists = False
        
        for c in new_card_pol:
            if c[0] == num and c[1] == tip:
                exists = True
                break
            elif c[0] == num and num == "A":
                exists = True
                break
        
        if not exists:
            new_card_pol.append([num, tip])
            total_value += card_value(num)
    
    return new_card_pol

def deal_card(e):
    global all_card_pol
    if e == 0:
        global player_card_pol, player_score, player_score_alt
        
        card = all_card_pol.pop()
        player_card_pol.append(card)
        
        score = card_value(card[0])
        
        player_score += score
        
        if score == 1:
            player_score_alt += 11
        else:
            player_score_alt += score
        
        if player_score_alt > 21:
            player_score_alt = player_score
    else:
        global bot_card_pol, bot_score, bot_score_alt
        
        card = all_card_pol.pop()
        bot_card_pol.append(card)
        
        score = card_value(card[0])
        
        bot_score += score
        
        if score == 1:
            bot_score_alt += 11
        else:
            bot_score_alt += score
        
        if bot_score_alt > 21:
            bot_score_alt = bot_score

def draw_0(x, y, api):
    api["display"].vline(x + 4, y + 2, 5, 1)
    api["display"].hline(x + 2, y + 4, 5, 1)
        
    api["display"].vline(x + 9, y + 19, 5, 1)
    api["display"].hline(x + 7, y + 21, 5, 1)

def draw_1(x, y, api):
    api["display"].vline(x + 4, y + 2, 4, 1)
    api["display"].hline(x + 2, y + 6, 5, 1)
    api["display"].vline(x + 3, y + 3, 2, 1)
    api["display"].vline(x + 5, y + 3, 2, 1)
        
    api["display"].vline(x + 9, y + 19, 4, 1)
    api["display"].hline(x + 7, y + 23, 5, 1)
    api["display"].vline(x + 8, y + 20, 2, 1)
    api["display"].vline(x + 10, y + 20, 2, 1)
    
def draw_2(x, y, api):
    api["display"].vline(x + 4, y + 2, 5, 1)
    api["display"].hline(x + 2, y + 4, 5, 1)
    api["display"].vline(x + 3, y + 3, 3, 1)
    api["display"].vline(x + 5, y + 3, 3, 1)
        
    api["display"].vline(x + 9, y + 19, 5, 1)
    api["display"].hline(x + 7, y + 21, 5, 1)
    api["display"].vline(x + 8, y + 20, 3, 1)
    api["display"].vline(x + 10, y + 20, 3, 1)
    
def draw_3(x, y, api):
    api["display"].vline(x + 2, y + 3, 2, 1)
    api["display"].vline(x + 3, y + 2, 4, 1)
    api["display"].vline(x + 4, y + 3, 4, 1)
    api["display"].vline(x + 5, y + 2, 4, 1)
    api["display"].vline(x + 6, y + 3, 2, 1)
        
    api["display"].vline(x + 7, y + 20, 2, 1)
    api["display"].vline(x + 8, y + 19, 4, 1)
    api["display"].vline(x + 9, y + 20, 4, 1)
    api["display"].vline(x + 10, y + 19, 4, 1)
    api["display"].vline(x + 11, y + 20, 2, 1)

def draw_card(x, y, c, api):
    api["display"].rect(x, y, 14, 27, 1)
    api["display"].text(str(c[0]), x + 3, y + 10, 1)
    
    if c[1] == 0:
        draw_0(x, y, api)
    elif c[1] == 1:
        draw_1(x, y, api)
    elif c[1] == 2:
        draw_2(x, y, api)
    else:
        draw_3(x, y, api)

def draw_card_hidden(x, y, api):
    api["display"].rect(x, y, 14, 27, 1)
    api["display"].line(x + 1, y + 1, x + 12, y + 25, 1)
    api["display"].line(x + 1, y + 25, x + 12, y + 1, 1)

def run(api):
    global b_won, p_won, total, turn, player_card_pol, bot_card_pol, all_card_pol, selected, buttons_count, move_delay, bet
    global player_score, player_score_alt, bot_score, bot_score_alt
    
    if p_won and b_won:
        api["display"].text("Draw", 2, 60, 1)
    elif p_won:
        api["display"].text("You Won!", 2, 60, 1)
    elif b_won:
        api["display"].text("Dealer Won", 2, 60, 1)
    
    if (p_won or b_won) and move_delay <= 0:
        if p_won and b_won:
            total += bet
        elif p_won:
            total += int(bet * 2)
        
        p_won = False
        b_won = False
        player_card_pol = []
        bot_card_pol = []
        player_score = player_score_alt = 0
        bot_score = bot_score_alt = 0
        turn = -1
        selected = 0
    
    if not api["in_bar"]:
        if api["up"][0] == "released" or api["left"][0] == "released":
            api["play_wav"]("click.wav")
            selected += 1
            selected = selected % buttons_count
        elif api["down"][0] == "released" or api["right"][0] == "released":
            api["play_wav"]("click.wav")
            selected -= 1
            selected = selected % buttons_count
    
    if turn == -1:
        buttons_count = 3
        
        api["display"].text(str(bet) + "$", 2, 89, 1)
        
        if selected == 0:
            api["display"].fill_rect(2, 98, 28, 13, 1)
            api["display"].text("BET", 4, 100, 0)
        else:
            api["display"].rect(2, 98, 28, 13, 1)
            api["display"].text("BET", 4, 100, 1)
        
        if selected == 1:
            api["display"].fill_rect(2, 114, 13, 13, 1)
            api["display"].text("<", 4, 117, 0)
        else:
            api["display"].rect(2, 114, 13, 13, 1)
            api["display"].text("<", 4, 117, 1)
        
        if selected == 2:
            api["display"].fill_rect(17, 114, 13, 13, 1)
            api["display"].text(">", 20, 117, 0)     
        else:
            api["display"].rect(17, 114, 13, 13, 1)
            api["display"].text(">", 20, 117, 1)
        
        if not api["in_bar"]:
        
            if api["ok"][0] == "pressed" or (api["ok"][0] == "down" and api["ok"][1] % 3 == 0 and api["ok"][1] != 0):
                if selected == 0 and total >= bet:
                    api["play_wav"]("select.wav")
                    total -= bet
                    turn = 0
                    all_card_pol = create_pol()
                
                    deal_card(0)
                    deal_card(0)
                
                    deal_card(1)
                    move_delay = 5
                
                elif selected == 1 and bet > 10:
                    bet -= 10
                elif selected == 2 and bet < total:
                    bet += 10
        
    elif turn == 0 and not p_won and not b_won and move_delay <= 0:
        buttons_count = 2
        
        api["display"].text(str(bet) + "$", 2, 89, 1)
        
        if selected == 0:
            api["display"].fill_rect(2, 98, 28, 13, 1)
            api["display"].text("HIT", 4, 100, 0)        
        else:
            api["display"].rect(2, 98, 28, 13, 1)
            api["display"].text("HIT", 4, 100, 1)
        
        if selected == 1:
            api["display"].fill_rect(2, 114, 36, 13, 1)
            api["display"].text("STAY", 4, 117, 0)        
        else:
            api["display"].rect(2, 114, 36, 13, 1)
            api["display"].text("STAY", 4, 117, 1)
            
        if api["ok"][0] == "pressed" and not api["in_bar"]:
            api["play_wav"]("select.wav")
            
            if selected == 0:
                move_delay = 5
                deal_card(0)
                
                if player_score > 21 and player_score_alt > 21:
                    b_won = True
                    api["play_wav"]("loose.wav")
                    move_delay = 20
                elif player_score == 21 or player_score_alt == 21:
                    p_won = True
                    api["play_wav"]("win.wav")
                    move_delay = 20
            
            elif selected == 1:
                turn = 2
        
    elif move_delay <= 0 and not p_won and not b_won:
        move_delay = 10
        
        if bot_score < 17 and bot_score_alt < 17:
            deal_card(1)
            
            if bot_score > 21 and bot_score_alt > 21:
                api["play_wav"]("win.wav")
                p_won = True
                move_delay = 20
            elif bot_score == 21 or bot_score_alt == 21:
                api["play_wav"]("loose.wav")
                b_won = True
                move_delay = 20
        else:
            if (bot_score > player_score and bot_score > player_score_alt) or (bot_score_alt > player_score and bot_score_alt > player_score_alt):
                api["play_wav"]("loose.wav")
                b_won = True
                move_delay = 20
            elif (player_score > bot_score and player_score > bot_score_alt) or (player_score_alt > bot_score and player_score_alt > bot_score_alt):
                api["play_wav"]("win.wav")
                p_won = True
                move_delay = 20
            else:
                b_won = p_won = True
                move_delay = 20
    
    if move_delay > 0:
        move_delay -= 1
    
    if turn != -1:
        px, py = 110, 100
        
        for c in player_card_pol:
            draw_card(px, py, c, api)
            px -= 15
        
        p_sc_text = ""
        
        if player_score == player_score_alt:
           p_sc_text = f"{player_score:>5}"
        else:
            p_sc_text = f"{player_score}/{player_score_alt}"
            p_sc_text = f"{p_sc_text:>5}"
        
        api["display"].text(p_sc_text, 85, 90, 1)
        
        bx, by = 3, 14
        
        for c in bot_card_pol:
            draw_card(bx, by, c, api)
            bx += 15
            
        if len(bot_card_pol) == 1:
            draw_card_hidden(bx, by, api)
        
        b_sc_text = ""
        
        if bot_score == bot_score_alt:
           b_sc_text = f"{bot_score:<5}"
        else:
            b_sc_text = f"{bot_score}/{bot_score_alt}"
            b_sc_text = f"{b_sc_text:<5}"
            
        api["display"].text(b_sc_text, 2, 43, 1)
    
    api["display"].text(str(total) + "$", 2, 73, 1)
    
    return True
            