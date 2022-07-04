import pygame, keyboard, random, time, os
from tetrominoes import *

pygame.font.init()

s_width, s_height = 800, 700
play_width, play_height = 300, 600  
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 15

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128), (255, 0, 0),
                (255, 162, 0), (0, 188, 255), (0, 0, 255), (0, 255, 0), (100, 100, 100)]

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Piece(object):
    def __init__(self, x, y, shape):
        self.x, self.y = x, y
        self.shape, self.color = shape, shape_colors[shapes.index(shape)]
        self.rotation = 0

def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j, i)]
                grid[i][j] = c
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column  == "0": positions.append((shape.x + j, shape.y + i))
    for i, pos in enumerate(positions): positions[i] = (pos[0]-2, pos[1]-4)

    return positions

def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1: return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1: return True
    return False

def draw_gave_over(surface):
    font = pygame.font.Font(resource_path("font.ttf"), 120)
    label = font.render("GAVE OVER!", 1, (255, 0, 0))
    surface.blit(label, (s_width/2-label.get_width()/2, s_height/2-label.get_height()/2))

def get_shape(shapes):
    return Piece(5, 0, random.choice(shapes))
   
def draw_grid(surface, grid):
    sx, sy = top_left_x, top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (40, 40, 40), (sx, sy+i*block_size), (sx+play_width, sy+i*block_size))
        for j in range(len(grid[i])): pygame.draw.line(surface, (40, 40, 40), (sx+j*block_size, sy), (sx+j*block_size, sy+play_height))
                
def clear_rows(grid, locked, score):
    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try: del locked[(j, i)]
                except: continue
    if inc > 0:
        if inc == 1: score += 40
        if inc == 2: score += 100
        if inc == 3: score += 300
        if inc >= 4: score += 1200
        play_audio("rowclear.mp3", 2, 1)
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return score

def draw_next_shape(shape, surface):
    font = pygame.font.Font(resource_path("font.ttf"), 20)
    label = font.render("Next Shape:", 1, (255, 255, 0))

    sx = top_left_x + play_width+50
    sy = top_left_y + play_height/7
    format = shape.shape[shape.rotation % len(shape.shape)]

    pygame.draw.rect(surface, (255, 255, 255), (sx-3, sy-3, 155, 155), 4)
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                subcolor = (shape.color[0]/1.5, shape.color[1]/1.5, shape.color[2]/1.5)
                pygame.draw.rect(surface, shape.color, (sx+j*block_size, sy+i*block_size, block_size, block_size), 0)
                pygame.draw.rect(surface, subcolor, (sx+j*block_size+block_size/4, sy+i*block_size+block_size/4, block_size/2, block_size/2), 0)
    surface.blit(label, (sx+5, sy-30))

def draw_stats(surface, score, highscore):
    font = pygame.font.Font(resource_path("font.ttf"), 20)
    
    lbl_score = font.render(f"Score:", 1, (255, 255, 0))
    lbl_scoreNum = font.render(f"{score}", 1, (255, 255, 0))
    lbl_highscore = font.render(f"Highscore:", 1, (255, 255, 0))
    lbl_highscoreNum = font.render(f"{highscore}", 1, (255, 255, 0))
    
    sx = top_left_x + play_width+50
    sy = top_left_y + play_height/2
    
    surface.blit(lbl_score, (sx+5, sy))
    surface.blit(lbl_scoreNum, (sx+5, sy+30))
    surface.blit(lbl_highscore, (sx+5, sy+80))
    surface.blit(lbl_highscoreNum, (sx+5, sy+110))
    pygame.draw.rect(surface, (255, 255, 255), (sx-3, sy+25, 155, 30), 4)
    pygame.draw.rect(surface, (255, 255, 255), (sx-3, sy+105, 155, 30), 4)

def draw_window(surface, grid):
    surface.fill((0, 0, 0))

    font = pygame.font.Font(resource_path("font.ttf"), 50)
    label = font.render("Tetris 5011", 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), 30))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            subcolor = (grid[i][j][0]/1.5, grid[i][j][1]/1.5, grid[i][j][2]/1.5)
            pygame.draw.rect(surface, grid[i][j], (top_left_x+j*block_size, top_left_y+i*block_size, block_size, block_size), 0)
            pygame.draw.rect(surface, subcolor, (top_left_x+j*block_size+block_size/4+1, top_left_y+i*block_size+block_size/4+1, block_size/2, block_size/2), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 4)
    
    draw_grid(surface, grid)

def save_stats(highscore):
    try:
        if os.path.exists("C:/Windows/Temp/tetris_data.dat"):        
            open("C:/Windows/Temp/tetris_data.dat", "w").close()
            
            f = open("C:/Windows/Temp/tetris_data.dat", "a")
            f.write(str(highscore))
            f.close()
        else:
            f = open("C:/Windows/Temp/tetris_data.dat", "a")
            f.write(str(highscore))
            f.close()
    except: pass

def load_stats():
    try: 
        if os.path.exists("C:/Windows/Temp/tetris_data.dat"):
            f = open("C:/Windows/Temp/tetris_data.dat", "r")
            highscore = f.read()
        else:
            f = open("C:/Windows/Temp/tetris_data.dat", "a")
            f.write("0")
            f.close()
            highscore = 0
        if highscore == "": highscore = 0
        return highscore
    except: pass

def stop_audio():
    for i in range(0, 7):
        try: pygame.mixer.Channel(i).stop()
        except: pass
        
def play_audio(file, channel, volume, loop=False):
    file = resource_path(file)
    try:
        pygame.mixer.pre_init(); pygame.mixer.init(); pygame.init()
        if loop: pygame.mixer.Channel(channel).play(pygame.mixer.Sound(file), -1)
        else: pygame.mixer.Channel(channel).play(pygame.mixer.Sound(file))
        pygame.mixer.Channel(channel).set_volume(volume)
    except: pass

def resize():
    global s_width, s_height, top_left_x, top_left_y

    s_width, s_height = pygame.display.get_surface().get_size()
    top_left_x = (s_width - play_width) // 2
    top_left_y = s_height - play_height - 15

def main(win, difficulty):
    adjust_difficulty(difficulty)
    locked_positions = {}
    grid = create_grid(locked_positions)

    run = True
    change_piece, current_piece, next_piece = False, get_shape(shapes), get_shape(shapes)
    score, highscore = 0, 0
    clock = pygame.time.Clock()
    fall_time, fall_speed, level_time = 0, 0.27, 0
    highscore = int(load_stats())
    
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick(); resize()
        time.sleep(0.1)

        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                run = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1

        if keyboard.is_pressed("A"):
            current_piece.x -= 1
            if not(valid_space(current_piece, grid)):
                current_piece.x += 1
        if keyboard.is_pressed("D"):
            current_piece.x += 1
            if not(valid_space(current_piece, grid)):
                current_piece.x -= 1
        if keyboard.is_pressed("S"):
            current_piece.y += 1
            if not(valid_space(current_piece, grid)):
                current_piece.y -= 1

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape(shapes)
            change_piece = False
            score = clear_rows(grid, locked_positions, score)

        draw_window(win, grid)
        draw_next_shape(next_piece, win)
        draw_stats(win, score, highscore)
        pygame.display.update()

        if check_lost(locked_positions):
            stop_audio()
            if score > highscore: save_stats(score)
            draw_gave_over(win)
            wait = 100
            while wait>0:
                clock.tick(); resize(); time.sleep(0.1); pygame.event.get()
                pygame.display.update(); wait -= 1
            run = False

def adjust_difficulty(difficulty):
    global shapes
    
    if difficulty == 0:
        shapes = [S, Z, I, O, J, L, T]
        play_audio("soundtrack.mp3", 1, 0.1, True)
        
    if difficulty == 1:
        shapes = [S, Z, I, O, J, L, T, i, v, V]
        play_audio("soundtrack.mp3", 1, 0.1, True)
        
    if difficulty == 2:
        shapes = [S, Z, I, O, J, L, T, i, v, V, u, U, z]
        play_audio("soundtrack.mp3", 1, 0.1, True)
        
    if difficulty == 3:
        shapes = [S, Z, I, O, J, L, T, i, v, V, u, U, z]
        play_audio("korobeiniki.mp3", 1, 0.2, True)

def draw_menu(surface, diff, diffs, diffcols):
    surface.fill((0, 0, 0))
    
    difftxt, diffcolor = diffs[diff], diffcols[diff]
    
    font = pygame.font.Font(resource_path("font.ttf"), 50)
    lbl_title = font.render("Tetris 5011", 1, (255, 255, 255))
    font = pygame.font.Font(resource_path("font.ttf"), 30)
    lbl_enter = font.render("Press Enter To Start", 1, (255, 255, 0))
    lbl_note = font.render("Press Space To Change Difficulty", 1, (255, 255, 255))
    lbl_diff = font.render(f"{difftxt}", 1, diffcolor)

    surface.blit(lbl_title, (top_left_x + play_width/2 - (lbl_title.get_width()/2), s_height/10))
    surface.blit(lbl_enter, (top_left_x + play_width/2 - (lbl_enter.get_width()/2), s_height/3))
    surface.blit(lbl_note, (top_left_x + play_width/2 - (lbl_note.get_width()/2), s_height/2.5))
    surface.blit(lbl_diff, (top_left_x + play_width/2 - (lbl_diff.get_width()/2), s_height/1.5))

def main_menu(win):
    run = True
    difficulty = 0
    diffcols = [(200, 200, 200), (255, 0, 0), (255, 0, 255), (0, 255, 255)]
    diffs = ["< Normal >", "< Hard >", "< Expert >", "< RUSSIAN >"]

    while run:
        resize(); draw_menu(win, difficulty, diffs, diffcols)
        time.sleep(0.1)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    difficulty += 1
                    if difficulty >= len(diffs): difficulty = 0
        
        if keyboard.is_pressed("Enter"):
            try: main(win, difficulty)
            except: run = False

win = pygame.display.set_mode((s_width, s_height), pygame.RESIZABLE)
pygame.display.set_caption("Tetris By Nick")

main_menu(win)
