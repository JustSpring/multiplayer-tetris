import pygame
import random
import time
import sys
import copy
import sqlite3
import csv
import os
from general_data import shapes, names

# Removed network/protocol imports

# Base resolution for design
BASE_WIDTH = 1920
BASE_HEIGHT = 1080

# Initialize Pygame and set up full screen display
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("SpringTile Tetris - Singleplayer Triple Mode")
clock = pygame.time.Clock()
screen_width, screen_height = screen.get_width(), screen.get_height()

# Compute scale factor based on base resolution.
scale = min(screen_width / BASE_WIDTH, screen_height / BASE_HEIGHT)

# Constants for grid dimensions
WIDTH_G = 10  # blocks per row
HEIGHT_G = 21  # blocks per column

# Block dimensions (scaled from a base of 32)
WIDTH_B = int(32 * scale)
HEIGHT_B = int(32 * scale)

# Colors remain the same.
COLORS = {
    1: (0, 255, 255), 2: (0, 0, 255), 3: (255, 127, 0), 4: (255, 255, 0),
    5: (0, 255, 0), 6: (128, 0, 128), 7: (255, 0, 0), 8: (150, 150, 150)
}

# Set up CSV logging.
log_filename = "tetris_log.csv"
log_file_exists = os.path.exists(log_filename) and os.path.getsize(log_filename) > 0
log_file = open(log_filename, "a", newline="")
log_writer = csv.writer(log_file)
if not log_file_exists:
    log_writer.writerow(["time", "screen", "button", "score", "score2"])
    log_file.flush()


def log_move(screen_id, button, score, score2):
    """Log a move (or periodic status) to the CSV file with an extra score2 value."""
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    log_writer.writerow([current_time, screen_id, button, score, score2])
    log_file.flush()


def start_screen():
    """Display the welcome start screen until a key is pressed."""
    screen.fill((180, 180, 180))
    title_font = pygame.font.Font('freesansbold.ttf', int(50 * scale))
    instr_font = pygame.font.Font('freesansbold.ttf', int(20 * scale))
    title_surface = title_font.render("SpringTile Tetris", True, (0, 0, 0))
    instr_surface = instr_font.render("Press any key to continue", True, (0, 0, 0))
    screen.blit(title_surface, ((screen_width - title_surface.get_width()) // 2, screen_height // 4))
    screen.blit(instr_surface, ((screen_width - instr_surface.get_width()) // 2, screen_height // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        clock.tick(30)


def mode_selection_screen():
    """Display the mode selection screen and wait for user to choose 1 or 3 players."""
    screen.fill((180, 180, 180))
    title_font = pygame.font.Font('freesansbold.ttf', int(50 * scale))
    instr_font = pygame.font.Font('freesansbold.ttf', int(20 * scale))
    title_surface = title_font.render("Select Game Mode", True, (0, 0, 0))
    mode_instr = instr_font.render("Press 1 for One Player Mode | Press 3 for Three Player Mode", True, (0, 0, 0))
    screen.blit(title_surface, ((screen_width - title_surface.get_width()) // 2, screen_height // 4))
    screen.blit(mode_instr, ((screen_width - mode_instr.get_width()) // 2, screen_height // 2))
    pygame.display.flip()
    mode = None
    while mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = 1
                elif event.key == pygame.K_3:
                    mode = 3
        clock.tick(30)
    return mode


# --- Control Mapping ---
# Arrow keys now control piece movement:
CONTROL_ROTATE = pygame.K_UP     # Rotate with the Up arrow
CONTROL_LEFT = pygame.K_LEFT     # Move left with the Left arrow
CONTROL_DOWN = pygame.K_DOWN     # Move down with the Down arrow
CONTROL_RIGHT = pygame.K_RIGHT   # Move right with the Right arrow
CONTROL_HOLD = pygame.K_LSHIFT
CONTROL_HARD_DROP = pygame.K_SPACE

# A and D keys are used to switch the active game (only in three-player mode):
SWITCH_LEFT = pygame.K_a
SWITCH_RIGHT = pygame.K_d


class Game:
    def __init__(self, offset=(50, 60)):
        # Scale the offsets.
        self.UpperLeft = (int(offset[0] * scale), int(offset[1] * scale))
        self.PrevUpperLeft = (self.UpperLeft[0] + int(400 * scale), self.UpperLeft[1])
        self.HoldUpperLeft = (self.UpperLeft[0] + int(400 * scale), self.UpperLeft[1] + int(200 * scale))
        self.cells = [[0 for _ in range(WIDTH_G)] for _ in range(HEIGHT_G)]
        self.points = 0
        self.pieceLis = [0, 1, 2, 3, 4, 5, 6]
        self.piece = None
        self.nextPiece = None
        self.holdPiece = None
        self.can_hold = True
        self.speed_time = 0.75
        self.alive = True
        # Timing for continuous movement:
        self.last_move_R = time.time()
        self.last_move_L = time.time()
        self.last_move_D = time.time()
        self.last_fall = time.time()
        self.name = random.choice(names)
        self.first_piece()

    def first_piece(self):
        num = random.choice(self.pieceLis)
        self.pieceLis.remove(num)
        self.nextPiece = Piece(shapes[num])
        self.getNextPiece()

    def getNextPiece(self):
        if len(self.pieceLis) == 0:
            self.pieceLis = [0, 1, 2, 3, 4, 5, 6]
        num = random.choice(self.pieceLis)
        self.pieceLis.remove(num)
        self.piece = self.nextPiece
        self.nextPiece = Piece(shapes[num])
        self.can_hold = True

    def get_best(self):
        con = sqlite3.connect("data.db")
        con.execute('''CREATE TABLE IF NOT EXISTS data(
            NAME TEXT,
            SCORE INTEGER
        );''')
        cur = con.execute('SELECT * FROM data;')
        max_value, max_name = 0, "null"
        for line in cur:
            if line[1] > max_value:
                max_value, max_name = line[1], line[0]
        con.close()
        return max_value, max_name

    def add_score(self, name, score):
        con = sqlite3.connect("data.db")
        con.execute('INSERT INTO data(NAME, SCORE) VALUES(?,?);', (name, score))
        con.commit()
        con.close()

    def checkAndRemoveRow(self):
        rows = [y for y, row in enumerate(self.cells) if all(column != 0 for column in row)]
        self.points += [0, 100, 300, 500, 800][len(rows)]
        for row in rows:
            row -= rows.index(row)
            self.cells[row:HEIGHT_G - 1] = self.cells[row + 1:HEIGHT_G]
            self.cells[HEIGHT_G - 1] = [0] * WIDTH_G
        return len(rows)

    def printBlock(self, startPos, x, y, color):
        bx = startPos[0] + x * WIDTH_B + 1
        by = startPos[1] + (HEIGHT_G - y) * HEIGHT_B
        pygame.draw.rect(screen, (0, 0, 50), (bx, by, WIDTH_B, HEIGHT_B))
        pygame.draw.rect(screen, color, (bx, by, WIDTH_B - int(3 * scale), HEIGHT_B - int(3 * scale)))

    def printBlockPrev(self, x, y, color, outline):
        bx = self.PrevUpperLeft[0] + x * WIDTH_B + 1
        by = self.PrevUpperLeft[1] + (4 - y) * HEIGHT_B
        if outline:
            pygame.draw.rect(screen, (0, 0, 50), (bx, by, WIDTH_B, HEIGHT_B))
            pygame.draw.rect(screen, color, (bx, by, WIDTH_B - int(3 * scale), HEIGHT_B - int(3 * scale)))
        else:
            pygame.draw.rect(screen, color, (bx, by, WIDTH_B, HEIGHT_B))

    def printBlockHold(self, x, y, color, outline):
        bx = self.HoldUpperLeft[0] + x * WIDTH_B + 1
        by = self.HoldUpperLeft[1] + (4 - y) * HEIGHT_B
        if outline:
            pygame.draw.rect(screen, (0, 0, 50), (bx, by, WIDTH_B, HEIGHT_B))
            pygame.draw.rect(screen, color, (bx, by, WIDTH_B - int(3 * scale), HEIGHT_B - int(3 * scale)))
        else:
            pygame.draw.rect(screen, color, (bx, by, WIDTH_B, HEIGHT_B))

    def printPreview(self):
        startPos = (self.piece.position[0], self.piece.position[1])
        while self.checkMove():
            self.piece.position = (self.piece.position[0], self.piece.position[1] - 1)
        if (self.piece.position[0], self.piece.position[1]) == startPos:
            return
        self.piece.position = (self.piece.position[0], self.piece.position[1] + 1)
        y = self.piece.position[1]
        for posY in range(3, -1, -1):
            x = self.piece.position[0]
            for posX in range(4):
                if self.piece.getPiece()[posY][posX] == 1:
                    self.printBlock(self.UpperLeft, x, y, (40, 40, 40))
                x += 1
            y += 1
        self.piece.position = startPos

    def printNext(self):
        for y in range(-1, 4):
            for x in range(-1, 4):
                self.printBlockPrev(x, y, (200, 200, 200), False)
        for posY, row in enumerate(self.nextPiece.getPiece()[::-1]):
            for posX, column in enumerate(row):
                if column == 1:
                    self.printBlockPrev(posX, posY, COLORS[self.nextPiece.shape.color], True)

    def printHold(self):
        for y in range(-1, 4):
            for x in range(-1, 4):
                self.printBlockHold(x, y, (200, 200, 200), False)
        if self.holdPiece:
            for posY, row in enumerate(self.holdPiece.getPiece()[::-1]):
                for posX, column in enumerate(row):
                    if column == 1:
                        self.printBlockHold(posX, posY, COLORS[self.holdPiece.shape.color], True)

    def printScore(self):
        font = pygame.font.Font('freesansbold.ttf', int(20 * scale))
        self._draw_score_text('Hold', int(10 * scale), int(-30 * scale), font, base=self.HoldUpperLeft)
        self._draw_score_text(f'SCORE: {self.points}', int(10 * scale), int(120 * scale), font, base=self.UpperLeft)
        self._draw_score_text('Next', int(10 * scale), int(-30 * scale), font, base=self.PrevUpperLeft)

    def _draw_score_text(self, text, y, x, font, base):
        text_surface = font.render(text, True, (0, 0, 0))
        textRect = text_surface.get_rect()
        textRect.y, textRect.x = base[1] + y, base[0] + x
        screen.blit(text_surface, textRect)

    def printScreen(self, active=False):
        # Draw the board.
        for y in range(HEIGHT_G):
            for x in range(WIDTH_G):
                self.printBlock(self.UpperLeft, x, y, (0, 0, 0))
        y_index = 0
        for row in self.cells:
            x_index = 0
            for column in row:
                if column != 0:
                    color = COLORS[column % 10]
                    self.printBlock(self.UpperLeft, x_index, y_index, color)
                x_index += 1
            y_index += 1
        self.printPreview()
        y = self.piece.position[1]
        for posY in range(3, -1, -1):
            x = self.piece.position[0]
            for posX in range(4):
                if self.piece.getPiece()[posY][posX] == 1:
                    self.printBlock(self.UpperLeft, x, y, COLORS[self.piece.shape.color])
                x += 1
            y += 1
        self.printNext()
        self.printHold()
        self.printScore()
        # If this board is active, draw a red outline around it.
        if active:
            outline_rect = pygame.Rect(self.UpperLeft[0], self.UpperLeft[1] + HEIGHT_B, WIDTH_G * WIDTH_B, HEIGHT_G * HEIGHT_B)
            pygame.draw.rect(screen, (255, 0, 0), outline_rect, max(1, int(5 * scale)))

    def checkMove(self):
        posY = 0
        for y in range(3, -1, -1):
            posX = 0
            for x in range(4):
                if self.piece.getPiece()[y][x] == 1:
                    new_x = self.piece.position[0] + posX
                    new_y = self.piece.position[1] + posY
                    if new_x < 0 or new_x >= WIDTH_G or new_y < 0 or new_y >= HEIGHT_G or self.cells[new_y][new_x] != 0:
                        return False
                posX += 1
            posY += 1
        return True

    def movePart(self, direction):
        if direction == "D":
            self.piece.position = (self.piece.position[0], self.piece.position[1] - 1)
            if not self.checkMove():
                self.piece.position = (self.piece.position[0], self.piece.position[1] + 1)
                self.connectPart()
                return True  # piece locked
        elif direction == "R":
            self.piece.position = (self.piece.position[0] + 1, self.piece.position[1])
            if not self.checkMove():
                self.piece.position = (self.piece.position[0] - 1, self.piece.position[1])
        elif direction == "L":
            self.piece.position = (self.piece.position[0] - 1, self.piece.position[1])
            if not self.checkMove():
                self.piece.position = (self.piece.position[0] + 1, self.piece.position[1])
        return False

    def allDown(self):
        while not self.movePart("D"):
            continue

    def rotate(self):
        temp = self.piece.rotation
        self.piece.rotate()
        if not self.checkMove():
            self.piece.rotation = temp
            self.piece.position = (self.piece.position[0] + 1, self.piece.position[1])
            self.piece.rotate()
            if self.checkMove():
                return
            self.piece.rotation = temp
            self.piece.position = (self.piece.position[0] - 2, self.piece.position[1])
            self.piece.rotate()
            if self.checkMove():
                return
            self.piece.position = (self.piece.position[0] + 1, self.piece.position[1])
            self.piece.rotation = temp

    def hold(self):
        if self.can_hold:
            if not self.holdPiece:
                self.holdPiece = self.piece
                self.getNextPiece()
            else:
                self.piece, self.holdPiece = self.holdPiece, self.piece
            self.piece.position = self.piece.getStartPosition()
            self.can_hold = False

    def connectPart(self):
        y = self.piece.position[1]
        for posY in range(3, -1, -1):
            x = self.piece.position[0]
            for posX in range(4):
                if self.piece.getPiece()[posY][posX] == 1:
                    self.cells[y][x] = self.piece.shape.color
                x += 1
            y += 1
        self.getNextPiece()
        if not self.checkMove():
            self.player_lost()

    def player_lost(self):
        self.alive = False

    # --- AI Score Computation Helpers ---
    def checkMove_piece(self, piece, grid):
        posY = 0
        for y in range(3, -1, -1):
            posX = 0
            for x in range(4):
                if piece.getPiece()[y][x] == 1:
                    new_x = piece.position[0] + posX
                    new_y = piece.position[1] + posY
                    if new_x < 0 or new_x >= WIDTH_G or new_y < 0 or new_y >= HEIGHT_G or grid[new_y][new_x] != 0:
                        return False
                posX += 1
            posY += 1
        return True

    def get_column_height(self, grid, column):
        row = HEIGHT_G
        while row > 0 and grid[row - 1][column] == 0:
            row -= 1
        return row

    def compute_score2(self):
        piece_copy = copy.deepcopy(self.piece)
        while self.checkMove_piece(piece_copy, self.cells):
            piece_copy.position = (piece_copy.position[0], piece_copy.position[1] - 1)
        piece_copy.position = (piece_copy.position[0], piece_copy.position[1] + 1)
        combined = copy.deepcopy(self.cells)
        y = piece_copy.position[1]
        for posY in range(3, -1, -1):
            x = piece_copy.position[0]
            for posX in range(4):
                if piece_copy.getPiece()[posY][posX] == 1:
                    if 0 <= y < HEIGHT_G and 0 <= x < WIDTH_G:
                        combined[y][x] = piece_copy.shape.color
                x += 1
            y += 1
        agg_height = sum(self.get_column_height(combined, col) for col in range(WIDTH_G))
        complete_lines = sum(1 for row in combined if all(val != 0 for val in row))
        filled = sum(1 for col in range(WIDTH_G) for row in combined if row[col] != 0)
        holes = agg_height - filled
        bumpiness = sum(
            abs(self.get_column_height(combined, col) - self.get_column_height(combined, col + 1))
            for col in range(WIDTH_G - 1)
        )
        score2 = (agg_height * -0.510066 +
                  complete_lines * 0.760666 +
                  holes * -0.35663 +
                  bumpiness * -0.184483)
        return score2


class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.rotation = 0
        self.position = self.getStartPosition()

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4

    def getPiece(self):
        return self.shape.getShape(self.rotation)

    def getStartPosition(self):
        all_empty = all(i == 0 for i in self.shape.getShape(self.rotation)[0])
        return (3, 17) if all_empty else (3, 16)


def restart(game):
    game.cells = [[0 for _ in range(WIDTH_G)] for _ in range(HEIGHT_G)]
    game.pieceLis = [0, 1, 2, 3, 4, 5, 6]
    game.holdPiece = None
    game.add_score(game.name, game.points)
    game.first_piece()
    game.speed_time = 0.75
    game.points = 0
    game.alive = True
    game.last_move_R = time.time()
    game.last_move_L = time.time()
    game.last_move_D = time.time()
    game.last_fall = time.time()


# Show the welcome start screen.
start_screen()
# Display mode selection screen.
mode = mode_selection_screen()

# Create game instance(s) based on the chosen mode.
if mode == 1:
    game1 = Game(offset=(50, 60))
    games = [game1]
else:  # mode == 3
    game1 = Game(offset=(50, 60))
    game2 = Game(offset=(650, 60))
    game3 = Game(offset=(1300, 60))
    games = [game1, game2, game3]

# Active game index (0-based)
active_game = 0

last_periodic_log = time.time()

# Main game loop.
while True:
    current_time = time.time()
    # Periodic logging for all games.
    if current_time - last_periodic_log >= 1:
        for idx, game in enumerate(games):
            log_move(str(idx+1), "time update", game.points, game.compute_score2())
        last_periodic_log = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # In three-player mode, allow switching the active game using A and D.
            if mode == 3:
                if event.key == SWITCH_LEFT:
                    active_game = (active_game - 1) % len(games)
                    continue
                elif event.key == SWITCH_RIGHT:
                    active_game = (active_game + 1) % len(games)
                    continue
            current = games[active_game]
            if event.key == CONTROL_ROTATE and current.alive:
                current.rotate()
                log_move(str(active_game+1), "rotate", current.points, current.compute_score2())
            if event.key == CONTROL_HARD_DROP:
                if current.alive:
                    current.allDown()
                    current.checkAndRemoveRow()
                    log_move(str(active_game+1), "hard_drop", current.points, current.compute_score2())
                else:
                    restart(current)
                    log_move(str(active_game+1), "restart", current.points, current.compute_score2())
            if event.key == CONTROL_HOLD and current.alive:
                current.hold()
                log_move(str(active_game+1), "hold", current.points, current.compute_score2())

    # Continuous movement for the active game.
    keys = pygame.key.get_pressed()
    current = games[active_game]
    if current.alive:
        if keys[CONTROL_RIGHT] and current_time - current.last_move_R > 0.07:
            current.movePart("R")
            current.last_move_R = current_time
            log_move(str(active_game+1), "right", current.points, current.compute_score2())
        if keys[CONTROL_LEFT] and current_time - current.last_move_L > 0.07:
            current.movePart("L")
            current.last_move_L = current_time
            log_move(str(active_game+1), "left", current.points, current.compute_score2())
        if keys[CONTROL_DOWN] and current_time - current.last_move_D > 0.07:
            current.movePart("D")
            current.checkAndRemoveRow()
            current.last_move_D = current_time
            log_move(str(active_game+1), "down", current.points, current.compute_score2())

    # --- Automatic falling for ALL games ---
    for game in games:
        if game.alive and current_time - game.last_fall >= game.speed_time:
            game.movePart("D")
            game.checkAndRemoveRow()
            game.last_fall = current_time

    # Clear the screen.
    screen.fill((255, 255, 255))
    # Draw each game board; highlight the active one.
    for idx, game in enumerate(games):
        game.printScreen(active=(idx == active_game))
    pygame.display.flip()
    clock.tick(30)
