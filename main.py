import random
import pygame
import os
import time
from personallib.camera import Camera
from personallib.canvas import *
from tile import Tile

# Constants
WIN_WIDTH = 800
WIN_HEIGHT = 800
FRAMERATE = 60
ICON_IMG = pygame.image.load(os.path.join("imgs", "icon.png"))
COLOURS = [(180, 180, 180), (50, 50, 50), (30, 60, 120), (255, 0, 0)]

# Pygame Setup
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Minesweeper")
pygame.display.set_icon(ICON_IMG)
clock = pygame.time.Clock()
pygame.font.init()

# Objects
cam = Camera(win, 0, 0, 1)
ui = Canvas(WIN_WIDTH, WIN_HEIGHT)
gameSurface = pygame.Surface((600, 600))
board = None

# Variables
running = True
started = False
gameOver = False
won = False
bombCount = 180
flagsRemaining = 0
timer = False
elapsed = [0, 0]

# Methods
def create_board(bombCount, excludePos=None):
    board = [[Tile((x, y)) for x in range(30)] for y in range(30)]
    excludeTile = board[excludePos[1]][excludePos[0]]
    exclusions = [board[pos[1]][pos[0]] for pos in excludeTile.neighbours] + [excludeTile] if excludePos else []
    bombs = 0
    while bombs < bombCount:
        tile = board[random.randint(0, 29)][random.randint(0, 29)]
        if not tile.bomb and tile not in exclusions:
            tile.bomb = True
            bombs += 1
    for i in range(30):
        for j in range(30):
            board[j][i].calculate_number(board)
    return board

def draw_game(cam, surface, board, gameOver):
    surface.fill((50, 50, 50))
    for i in range(30):
        for j in range(30):
            if board:
                pygame.draw.rect(surface, COLOURS[board[j][i].state], (i * 20 + 1, j * 20 + 1, 18, 18))
                if board[j][i].bomb and gameOver:
                    pygame.draw.circle(surface, COLOURS[3], (i * 20 + 10, j * 20 + 10), 5)   
                elif board[j][i].state == 1:
                    surface.blit(board[j][i].numberSurface, (i * 20 + 10 - (board[j][i].numberSurface.get_width() // 2), j * 20 + 10 - (board[j][i].numberSurface.get_height() // 2)))
            else:
                pygame.draw.rect(surface, COLOURS[0], (i * 20 + 1, j * 20 + 1, 18, 18))
    cam.blit(surface, (-300, -300))

def uncover_tile(board, tile):
    tile.state = 1
    if tile.number == 0:
        for pos in tile.neighbours:
            newTile = board[pos[1]][pos[0]]
            if newTile.state == 0:
                uncover_tile(board, board[pos[1]][pos[0]])

def strElapsed(elapsed):
    return "{:>2}:{:0>2}".format(*elapsed)

# UI
ui.add_element(Text("title", (100, 50), "georgia", 40, "Minesweeper", (255, 255, 255)))
ui.add_element(Text("timer", (700, 50), "georgia", 40, "0:00", (255, 255,255), "right"))
ui.add_element(Text("bombCounter", (700, 720), "georgia", 30, "", (255, 255, 255), "right"))

# Main Loop
previousTime = time.time()
if __name__ == '__main__':
    while running:
        
        clock.tick(FRAMERATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameOver:
                if event.button == 1:
                    mPos = cam.get_world_coord(pygame.mouse.get_pos())
                    relX = mPos[0] + 300
                    relY = mPos[1] + 300
                    if 0 <= relX <= 600 and 0 <= relY <= 600:
                        gridPos = (int(relX // 20), int(relY // 20))
                        if not started:
                            board = create_board(bombCount, gridPos)
                            flagsRemaining = bombCount
                            ui.find_element("bombCounter").render(f"{flagsRemaining}")
                            started = True
                            timer = True
                            previousTime = time.time()                            
                        tile = board[gridPos[1]][gridPos[0]]
                        if tile.state == 0:
                            if tile.bomb:
                                gameOver = True
                                timer = False
                            else:
                                uncover_tile(board, tile)
                elif event.button == 3 and started:
                    mPos = cam.get_world_coord(pygame.mouse.get_pos())
                    relX = mPos[0] + 300
                    relY = mPos[1] + 300
                    tile = board[int(relY // 20)][int(relX // 20)]
                    if 0 <= relX <= 600 and 0 <= relY <= 600 and tile.state % 2 == 0:
                        tile.state = (tile.state + 2) % 4
                        if tile.state == 0:
                            flagsRemaining += 1
                        else:
                            flagsRemaining -= 1
                        ui.find_element("bombCounter").render(f"{flagsRemaining}")
            elif event.type == pygame.KEYDOWN and gameOver:
                if event.key == pygame.K_r:
                    board = None
                    gameOver = False
                    started = False
                    won = False
                    elapsed = [0, 0]
                    ui.find_element("timer").render(strElapsed(elapsed))
                    ui.find_element("bombCounter").render("")
        if board:
            won = True
            for row in board:
                for tile in row:
                    if not tile.bomb and tile.state != 1:
                        won = False
        if won:
            gameOver = True

        executeTime = time.time()
        if timer and executeTime - previousTime >= 1:
            previousTime = executeTime
            elapsed[1] += 1
            if elapsed[1] == 60:
                elapsed[0] += 1
                elapsed[1] = 0
            ui.find_element("timer").render(strElapsed(elapsed))

        win.fill((0, 0, 0))

        draw_game(cam, gameSurface, board, gameOver)

        ui.update(cam)

        pygame.display.update()