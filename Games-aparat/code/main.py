import time, math, array, random, os, micropython, sys
from machine import Pin, I2C, I2S, lightsleep
import sh1107
from wavplayer import WavPlayer

try:
    import importlib
except:
    importlib = None

try:
    import traceback
except:
    traceback = None

micropython.alloc_emergency_exception_buf(128)

#screen variables
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)
display = sh1107.SH1107_I2C(128, 128, i2c, address=0x3C, rotate=90)

#MAX 98357A variables
DIN, BCLK, LRC, SD = 11, 12, 13, 14
amp_en = Pin(SD, Pin.OUT)
amp_en.value(1)
mute = False 

wp = WavPlayer(id=0, sck_pin=Pin(BCLK), ws_pin=Pin(LRC), sd_pin=Pin(DIN), ibuf=16384, root="/")

def make_sound(wav_dir): #making sound, checking for mute
    if mute:
        return
    
    if wp.isplaying(): #interupting the old sound if isplaying
        wp.stop_immediate()
    
    wp.play(wav_dir, loop=False)

api = {
    "display": display,
    "play_wav": make_sound,
    "up": ["up", 0, False], # states: up, pressed, down, released
    "down": ["up", 0, False],
    "left": ["up", 0, False],
    "right": ["up", 0, False],
    "ok": ["up", 0, False],
    "in_bar": False 
}

#buttons variables
B_MAP = [(10,"up"), (6,"down"), (7,"left"), (9,"right"), (8,"ok")]

temp_state_pressed = {"up": 0, "down": 0, "left": 0, "right": 0, "ok": 0}
temp_state_released = {"up": 0, "down": 0, "left": 0, "right": 0, "ok": 0}

GP_TO_NAME = {gp:name for gp,name in B_MAP} 
DEBOUNCE_MS = 25
_last = {gp:0 for gp,_ in B_MAP}
B_PINS = {}

def _apply(arg): #apply state from irq to temp state
    global api, temp_state_pressed, temp_state_released
    
    gp = arg >> 1
    pressed = (arg & 1)
    name = GP_TO_NAME[gp]
    
    if pressed:
        temp_state_pressed[name] = 1
    else:
        temp_state_released[name] = 1
    

def button_state_check():
    global api, temp_state_pressed, temp_state_released
    
    for b in ("up", "down", "left", "right", "ok"):
        state, frames, instant = api[b]
        
        p, r = temp_state_pressed[b], temp_state_released[b]
        
        if p or r: #transfer state from temp by irq to api
            temp_state_pressed[b] = 0
            temp_state_released[b] = 0
            
            if p and r:
                api[b][0] = "pressed"
                api[b][1] = 1
                api[b][2] = True
            elif p:
                api[b][0] = "pressed"
                api[b][1] = 1
                api[b][2] = False
            else:
                api[b][0] = "released"
                api[b][1] = 1
                api[b][2] = False
                
            continue
        
        if instant: #check if button should be instantly released
            api[b][0] = "released"
            api[b][1] = 1
            api[b][2] = False
            continue
        
        if state == "pressed" and api[b][1] >= 1: #button state sequence check
            api[b][0] = "down"
            api[b][1] = 0
        elif state == "released" and api[b][1] >= 1:
            api[b][0] = "up"
            api[b][1] = 0
        else:
            api[b][1] = frames + 1
        
        if B_PINS[b].value() == 1 and api[b][0] == "down": #unstuck check
            api[b][0] = "released"
            api[b][1] = 1

def _make_irq(gp): #irq for buttons
    
    def _irq(pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, _last[gp]) < DEBOUNCE_MS:
            return
    
        _last[gp] = now
        pressed = (pin.value() == 0)
    
        micropython.schedule(_apply, (gp << 1) | (1 if pressed else 0))
    
    return _irq

def buttons_init(): #create buttons
    for gp, name in B_MAP:
        p = Pin(gp, Pin.IN, Pin.PULL_UP)
        B_PINS[name] = p
        p.irq(handler=_make_irq(gp),trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

games = []
display_games = {} # ifneeded more space, make recycler view
selected_tile = 0
window = "Menu"

def get_games(): #get games dir only if has "run" function
    result = []
    
    for name in os.listdir('games'):
        if '.' in name:
            continue
        try:
            os.stat('games/{}/game.py'.format(name))
            result.append(name)
        except OSError:
            pass
    
    return sorted(result)

def load_game(name, api): #loading game as a lib
    mod_name = 'games.{}.game'.format(name)
    
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    
    if importlib:
        m = importlib.import_module(mod_name)
    else:
        m = __import__(mod_name)
        for part in mod_name.split('.')[1:]:
            m = getattr(m, part)
    
    if hasattr(m, 'init'): #check for init function, run if exists
        try:
            m.init(api)
        except Exception as _e:
            pass
    
    return m    

def draw_sound_button(r=1): #sound button drawing
    if r == 1:
        display.rect(113, 0, 11, 11, 1)
    else:
        display.fill_rect(113, 0, 11, 11, 1)
    display.fill_rect(115, 4, 3, 3, r)
    display.vline(119, 4, 3, r)
    display.vline(121, 2, 7, r)
    if mute:
        display.line(114, 1, 122, 9, r)
        
def draw_back_button(r=1): #back button drawing
    if r == 1:
        display.rect(100, 0, 11, 11, 1)
    else:
        display.fill_rect(100, 0, 11, 11, 1)
    
    display.text("<", 102, 2, r)

def display_main_content(name="Menu"): #top bar for menu and game
    display.text(name, 2, 0, 1)
    
    if name == "Menu":
        display_menu()
        
        if selected_tile != -1:
            draw_sound_button(1)
        elif selected_tile == -1:
            draw_sound_button(0)
            
    else:
        if selected_tile != -1:
            draw_sound_button(1)
        elif selected_tile == -1:
            draw_sound_button(0)
        if selected_tile != -2:
            draw_back_button(1)
        elif selected_tile == -2:
            draw_back_button(0)
    
    display.hline(0, 12, 128, 1)

def display_menu(): #menu item list
    y = 16
    
    for i, g in enumerate(games):
        line = ""
        if i == selected_tile:
            line += "> "
        else:
            line += "- "
        
        line += g
        
        display.text(line, 2, y, 1)
        y += 12

def main():
    global games, selected_tile, api, mute, window
    
    buttons_init() #create buttons
    games = get_games() #get games
    
    active_mod = None
    active_name = None
    keep = True
    
    while True:
        display.fill(0)
        
        #menu display and control
        if active_mod == None:
            
            window = "Menu"
            
            if api["up"][0] == "pressed":
                if selected_tile <= -1:
                    api["in_bar"] = False
                
                selected_tile -= 1
                
                make_sound("click.wav")
                if selected_tile < 0:
                    selected_tile = len(games) - 1
                    
            elif api["down"][0] == "pressed":
                if selected_tile <= -1:
                    api["in_bar"] = False 
                    
                selected_tile += 1
                
                make_sound("click.wav")
                if selected_tile > len(games) - 1:
                    selected_tile = 0
            
            if api["ok"][0] == "released" and selected_tile >= 0: #load the game
                active_name = games[selected_tile]
                active_mod = load_game(active_name, api)
                keep = True
                selected_tile = 0
                make_sound("select.wav")
        
        else: # run the "game" code
            window = active_name
            if not keep:
                active_mod = None
                active_name = None
                continue
            
            keep = True
            
            try:
                keep = active_mod.run(api)
            except Exception as e:
                display.fill(0)
                display.text("Game error", 20, 100, 1)
                if traceback:
                    traceback.print_exc()
                else:
                    sys.print_exception(e)
                keep = False
                display.show()
                time.sleep(2)
        
        if api["left"][0] == "down" and api["right"][0] == "down": #universal escape to top bar
            if api["left"][1] > 20 and api["right"][1] > 20:
                selected_tile = -1
                api["in_bar"] = True

        #top bar navigation
                
        if selected_tile == -1: 
            if api["ok"][0] == "released": #mute
                mute = not mute 
                make_sound("select.wav")
            
            if window != "Menu": 
                if api["left"][0] == "pressed" or api["right"][0] == "pressed":
                    selected_tile = -2
                    
            if api["down"][0] == "pressed": #exit top bar 
                selected_tile = 0
                api["in_bar"] = False 
        
        elif selected_tile == -2:
            if api["ok"][0] == "released": #exit "game"
                keep = False
                selected_tile = 0
                api["in_bar"] = False
                make_sound("select.wav")
            
            if api["left"][0] == "pressed" or api["right"][0] == "pressed":
                selected_tile = -1
            if api["down"][0] == "pressed": #exit top bar 
                selected_tile = 0
                api["in_bar"] = False
        
        #main display
        display_main_content(window)
        display.show()
        
        #state of buttons check
        button_state_check()
        time.sleep_ms(15)
        
main()