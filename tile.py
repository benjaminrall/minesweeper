import pygame

class Tile:

    pygame.font.init()
    FONT = pygame.font.SysFont("georgia", 16)

    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.bomb = False
        self.neighbours = self.calculate_neighbours()
        self.number = -1
        self.numberSurface = Tile.FONT.render("", True, (0, 0, 0))
        self.state = 0

    def calculate_neighbours(self):
        neighbours = []
        for ox in range (-1, 2):
            for oy in range(-1, 2):
                newX = self.x + ox
                newY = self.y + oy
                if 0 <= newX < 30 and 0 <= newY < 30:
                    neighbours.append((newX, newY))
        return neighbours

    def calculate_number(self, board):
        num = 0
        for neighbour in self.neighbours:
            if board[neighbour[1]][neighbour[0]].bomb:
                num += 1
        self.number = num
        if num > 0:
            self.numberSurface = Tile.FONT.render(f"{num}", True, (0, 0, 0))
