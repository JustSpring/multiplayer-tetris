import pygame
import random
import socket
import threading
import time
import sys
import copy
import sqlite3
from general_data import shapes, names
import protocol

# Constants
WIDTH_G = 10  # Number of blocks in each row
HEIGHT_G = 21  # Number of blocks in each column
WIDTH_B = 20
HEIGHT_B = 20
COLORS = {
    1: (0, 255, 255), 2: (0, 0, 255), 3: (255, 127, 0), 4: (255, 255, 0),
    5: (0, 255, 0), 6: (128, 0, 128), 7: (255, 0, 0), 8: (150, 150, 150)
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("SpringTile Tetris")
clock = pygame.time.Clock()


class Game:
    def __init__(self):
        self.cells = [[0 for _ in range(WIDTH_G)] for _ in range(HEIGHT_G)]
        self.UpperLeft = (50, 10)
        self.PrevUpperLeft = (300, 10)
        self.HoldUpperLeft = (300, 130)
        self.points = 0
        self.pieceLis = [0, 1, 2, 3, 4, 5, 6]
        self.piece = None
        self.nextPiece = None
        self.holdPiece = None
        self.sock = None
        self.opponentCells = {}
        self.startPosOppen = (500, 10)
        self.piece_rng = random.Random()
        self.players = {}
        self.name = random.choice(names)
        self.start = False
        self.connected = False
        self.opponent_block_width = None
        self.alive_opponent_positions = {1: [(500, 10, 20)], 2: [(500, 10, 15), (700, 10, 15)]}
        self.opponent_positions = {2: [(50, 10, 20), (500, 10, 20)], 3: [(50, 10, 15), (388, 10, 15), (726, 10, 15)]}
        self.ip = "127.0.0.1"
        self.alive = False
        self.restart = False
        self.can_hold = True
        self.places = None
        self.speed_time = 0.75
        self.solo = False

    def first_piece(self):
        num = self.piece_rng.choice(self.pieceLis)
        self.pieceLis.remove(num)
        self.nextPiece = Piece(shapes[num])
        self.getNextPiece()

    def connect(self, host, port):
        if not self.connected:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.connected = True
            threading.Thread(target=self.receive).start()
            self.send("SetName", self.name)
            self.send("GetSeed", "")

    def send(self, cmd, data):
        if self.solo:
            return
        try:
            self.sock.send(protocol.build_message(cmd, data))
        except:
            print("Failed to send data")

    def getNextPiece(self):
        if len(self.pieceLis) == 0:
            self.pieceLis = [0, 1, 2, 3, 4, 5, 6]
        num = self.piece_rng.choice(self.pieceLis)
        self.pieceLis.remove(num)
        self.piece = self.nextPiece
        self.nextPiece = Piece(shapes[num])
        self.can_hold = True

    def print_start(self):
        self.alive = True
        self.start = False
        screen.fill((180, 180, 180))
        font = pygame.font.Font('freesansbold.ttf', 20)
        ip_rect = pygame.Rect(100, 150, 180, 32)
        name_rect = pygame.Rect(300, 150, 180, 32)
        button = pygame.Rect(100, 200, 180, 40)
        start_rect = pygame.Rect(100, 250, 180, 40)
        solo_rect = pygame.Rect(100, 380, 180, 40)
        color_active = (100, 100, 200)
        color_passive = (0, 0, 0)
        active_ip = False
        active_name = False
        active_start = False
        active_connect = False
        active_solo = False

        while not self.start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("QUIT")
                    if self.sock:
                        self.sock.close()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    active_ip = ip_rect.collidepoint(event.pos)
                    active_connect = button.collidepoint(event.pos)
                    active_start = start_rect.collidepoint(event.pos)
                    active_name = name_rect.collidepoint(event.pos)
                    active_solo = solo_rect.collidepoint(event.pos)
                if event.type == pygame.KEYDOWN:
                    if active_ip and event.key == pygame.K_BACKSPACE:
                        self.ip = self.ip[:-1]
                    elif active_ip and len(self.ip) < 15:
                        self.ip += event.unicode
                    elif active_name and event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif active_name and len(self.name) < 15:
                        self.name += event.unicode

            self._draw_start_screen(
                ip_rect, name_rect, button, start_rect, solo_rect,
                color_active, color_passive, active_ip, active_name, active_connect, active_start, active_solo, font
            )
            if active_connect:
                self._attempt_connect()
                active_connect=False
            if active_start:
                self._attempt_start()
                active_start=False
            if active_solo:
                self.start = True
                self.solo = True
                active_solo = False
            clock.tick(30)

    def _draw_start_screen(
        self, ip_rect, name_rect, button, start_rect, solo_rect,
        color_active, color_passive, active_ip, active_name, active_connect, active_start, active_solo, font
    ):
        screen.fill((180, 180, 180))
        self._draw_text("Welcome!", 50, (100, 50))
        self._draw_text("Server IP:", 20, (100, 120))
        self._draw_text("Name:", 20, (300, 120))

        self._draw_button(button, "Connect", 20, active_connect, color_active, color_passive)
        self._draw_button(start_rect, "Start", 20, active_start, color_active, color_passive)
        self._draw_button(solo_rect, "PLAY SOLO", 20, active_solo, color_active, color_passive)

        self._draw_rect(ip_rect, active_ip, color_active, color_passive, font, self.ip)
        self._draw_rect(name_rect, active_name, color_active, color_passive, font, self.name)

        players_text = ", ".join([f"{self.players[key]} id={key}" for key in self.players])
        self._draw_text(players_text, 20, (100, 300))

        best_score = self.get_best()
        self._draw_text(f"Current Best: {best_score[1]} by {best_score[0]}", 20, (100, 350))

        pygame.display.flip()

    def _draw_text(self, text, size, position):
        font = pygame.font.Font('freesansbold.ttf', size)
        surface = font.render(text, True, (0, 0, 0))
        screen.blit(surface, position)

    def _draw_button(self, rect, text, size, active, color_active, color_passive):
        color = color_active if active else color_passive
        pygame.draw.rect(screen, color, rect)
        font = pygame.font.Font('freesansbold.ttf', size)
        surface = font.render(text, True, (255, 255, 255))
        text_x = rect.x + (rect.width - surface.get_width()) / 2
        text_y = rect.y + (rect.height - surface.get_height()) / 2
        screen.blit(surface, (text_x, text_y))


    def _draw_rect(self, rect, active, color_active, color_passive, font, text):
        color = color_active if active else color_passive
        pygame.draw.rect(screen, color, rect, 2)
        text_surface = font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (rect.x + 5, rect.y + 5))

    def _attempt_connect(self):
        try:
            self.connect(self.ip, 12345)
            self.send("GetPlayers", "")
        except:
            print("Error connecting")

    def _attempt_start(self):
        try:
            self.send("StartGame", "")
        except:
            print("Error starting game")

    def print_winners(self, winners):
        if not winners:
            winners = [""]
        self.alive = True
        self.start = False
        screen.fill((180, 180, 180))
        font = pygame.font.Font('freesansbold.ttf', 20)
        back_rect = pygame.Rect(100, 200, 180, 40)
        start_rect = pygame.Rect(100, 250, 180, 40)
        color_active = (100, 100, 200)
        color_passive = (0, 0, 0)
        active_start = False
        active_back = False
        texts = [
            "Nice try! Can you beat your score?", "Game over! You did great.", "So close! Want to try again?",
            "Well played! Ready for another round?", "That was intense! Let's go again.",
            "You're getting better! New PR next time?", "Keep stacking, keep cracking!",
            "The blocks didn't line up this time :("
        ]
        solo_text = random.choice(texts)

        while not self.start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("QUIT")
                    if self.sock:
                        self.sock.close()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    active_start = start_rect.collidepoint(event.pos)
                    active_back = back_rect.collidepoint(event.pos)

            self._draw_winner_screen(winners, solo_text, start_rect, back_rect, color_active, color_passive, active_start, active_back)
            if active_start:
                self._start_new_game()
                active_start = False
            if active_back:
                self._back_to_menu()
                active_back = False

    def _draw_winner_screen(self, winners, solo_text, start_rect, back_rect, color_active, color_passive, active_start, active_back):
        screen.fill((180, 180, 180))
        font = pygame.font.Font('freesansbold.ttf', 40)

        if self.solo:
            winners_surface = font.render(solo_text, True, (0, 0, 0))
            color = color_active if active_back else color_passive
            pygame.draw.rect(screen, color, back_rect)
            font = pygame.font.Font('freesansbold.ttf', 20)
            back_surface = font.render("Back to Menu", True, (255, 255, 255))
            screen.blit(back_surface, (back_rect.x + 20, back_rect.y + 10))

        else:
            winners_surface = font.render(f"The winner is {winners[0]}!", True, (0, 0, 0))
        screen.blit(winners_surface, (100, 50))

        if not self.solo:
            leaders_text = "Other places (first to last): " + " -- ".join(winners[1:])
            font = pygame.font.Font('freesansbold.ttf', 20)
            leaders_surface = font.render(leaders_text, True, (0, 0, 0))
            screen.blit(leaders_surface, (100, 120))
        else:
            self._draw_text(f"Your score: {self.points}", 20, (100, 120))
            best_score = self.get_best()
            self._draw_text(f"Current Best: {best_score[1]} by {best_score[0]}", 20, (100, 145))

        self._draw_button(start_rect, "Another Game", 20, active_start, color_active, color_passive)
        pygame.display.flip()

    def _start_new_game(self):
        if self.solo:
            self.start = True
            self.alive = True
        self.send("StartGame", "")

    def _back_to_menu(self):
        self.solo = False
        self.print_start()

    def get_best(self):
        con = sqlite3.connect("data.db")
        con.execute('''CREATE TABLE IF NOT EXISTS data(
            NAME TEXT,
            SCORE INTEGER
        );''')
        cur = con.execute(f'''SELECT * FROM data;''')
        max_value, max_name = 0, "null"
        for line in cur:
            if line[1] > max_value:
                max_value, max_name = line[1], line[0]
        return max_value, max_name

    def add_score(self, name, score):
        con = sqlite3.connect("data.db")
        con.execute('''INSERT INTO data(NAME, SCORE) VALUES(?,?);''', (name, score))
        con.commit()

    def checkAndRemoveRow(self):
        rows = [y for y, row in enumerate(self.cells) if all(column != 0 for column in row)]
        self.points += [0, 100, 300, 500, 800][len(rows)]
        for row in rows:
            row -= rows.index(row)
            self.cells[row:HEIGHT_G - 1] = self.cells[row + 1:HEIGHT_G]
            self.cells[HEIGHT_G - 1] = [0] * WIDTH_G
        if rows:
            self.send("UpdateRows", str(len(rows)))
        return len(rows)

    def printBlock(self, startPos, x, y, color):
        x = startPos[0] + x * WIDTH_B + 1
        y = startPos[1] + (HEIGHT_G - y) * HEIGHT_B
        pygame.draw.rect(screen, (0, 0, 50), (x, y, WIDTH_B, HEIGHT_B))
        pygame.draw.rect(screen, color, (x, y, WIDTH_B - 3, HEIGHT_B - 3))

    def print_block_opp(self, x, y, color):
        x = self.startPosOppen[0] + x * self.opponent_block_width + 1
        y = self.startPosOppen[1] + (HEIGHT_G - y) * self.opponent_block_width
        pygame.draw.rect(screen, (0, 0, 50), (x, y, self.opponent_block_width, self.opponent_block_width))
        pygame.draw.rect(screen, color, (x, y, self.opponent_block_width - 3, self.opponent_block_width - 3))

    def printBlockPrev(self, x, y, color, outline):
        x = self.PrevUpperLeft[0] + x * WIDTH_B + 1
        y = self.PrevUpperLeft[1] + (4 - y) * HEIGHT_B
        pygame.draw.rect(screen, (0, 0, 50), (x, y, WIDTH_B, HEIGHT_B)) if outline else None
        pygame.draw.rect(screen, color, (x, y, WIDTH_B - 3, HEIGHT_B - 3)) if outline else pygame.draw.rect(screen, color, (x, y, WIDTH_B, HEIGHT_B))

    def printBlockHold(self, x, y, color, outline):
        x = self.HoldUpperLeft[0] + x * WIDTH_B + 1
        y = self.HoldUpperLeft[1] + (4 - y) * HEIGHT_B
        if outline:
            if not self.can_hold:
                color = tuple(max(c - 80, 0) for c in color)
            pygame.draw.rect(screen, (0, 0, 50), (x, y, WIDTH_B, HEIGHT_B))
            pygame.draw.rect(screen, color, (x, y, WIDTH_B - 3, HEIGHT_B - 3))
        else:
            pygame.draw.rect(screen, color, (x, y, WIDTH_B, HEIGHT_B))

    def printScreen(self):
        screen.fill((255, 255, 255))
        if self.alive:
            for y in range(HEIGHT_G):
                for x in range(WIDTH_G):
                    self.printBlock(self.UpperLeft, x, y, (0, 0, 0))
            y = 0
            for row in self.cells:
                x = 0
                for column in row:
                    if column != 0:
                        color = COLORS[column % 10]
                        self.printBlock(self.UpperLeft, x, y, color)

                    x += 1
                y += 1
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

        self.printScreenOpponent()

    def printScreenOpponent(self):
        if len(self.opponentCells) <= 0:
            return
        if not self.alive and len(self.opponentCells) <= 1:
            return
        positions = self.alive_opponent_positions[len(self.opponentCells)] if self.alive else self.opponent_positions[len(self.opponentCells)]
        for current, key in enumerate(self.opponentCells):
            self.startPosOppen = (positions[current][0], positions[current][1])
            self.opponent_block_width = positions[current][2]
            for y in range(HEIGHT_G):
                for x in range(WIDTH_G):
                    self.print_block_opp(x, y, (0, 0, 0))
            for y, row in enumerate(self.opponentCells[key]):
                for x, column in enumerate(row):
                    if column != 0:
                        self.print_block_opp(x, y, COLORS[column % 10])

    def receive(self):
        while True:
            try:
                name, data = protocol.receive_data(self.sock)
                if name == "UpdateGrid":
                    self.opponentCells.update(data)
                elif name == "UpdateRows":
                    self.addLines(int(data))
                elif name == "SetSeed":
                    self.piece_rng.seed(float(data))
                elif name == "StartGame":
                    self.start = True
                    self.alive = True
                elif name == "SetPlayers":
                    self.players = data
                elif name == "DelPlayer" and int(data) in self.opponentCells:
                    del self.opponentCells[int(data)]
                    print(f"Deleted player id: {data}")
                elif name == "EndGame":
                    self.alive = False
                    self.send("EndGame", "")
                    print("Set restart to true")
                    self.restart = True
                elif name == "SetPlaces":
                    self.places = data
                elif name == "SetSpeed":
                    self.speed_time = float(data)
                    print(f"Speed updated to {data}")
            except:
                pass


    def crate_opp_cells(self):
        return_grid = copy.deepcopy(self.cells)
        if not return_grid:
            return [[0 for _ in range(WIDTH_G)] for _ in range(HEIGHT_G)]
        y = self.piece.position[1]
        for posY in range(3, -1, -1):
            x = self.piece.position[0]
            for posX in range(4):
                if self.piece.getPiece()[posY][posX] == 1 and y < len(return_grid) and x < len(return_grid[0]):
                    return_grid[y][x] = self.piece.shape.color
                x += 1
            y += 1
        return return_grid


    def printPreview(self):
        startPos = (self.piece.position[0], self.piece.position[1])
        while self.checkMove():
            self.piece.position = (self.piece.position[0], self.piece.position[1] - 1)
        if startPos == (self.piece.position[0], self.piece.position[1]):
            return False
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
        font = pygame.font.Font('freesansbold.ttf', 20)
        self._draw_score_text('Next', 10, 280, font)
        self._draw_score_text('Hold', 130, 280, font)
        self._draw_score_text(f'SCORE: {self.points}', 250, 280, font)

    def _draw_score_text(self, text, y, x, font):
        text_surface = font.render(text, True, (0, 0, 0))
        textRect = text_surface.get_rect()
        textRect.y, textRect.x = y, x
        screen.blit(text_surface, textRect)

    def checkMove(self):
        posY = 0
        for y in range(3, -1, -1):
            posX = 0
            for x in range(4):
                if self.piece.getPiece()[y][x] == 1 and (
                        self.piece.position[0] + posX < 0 or self.piece.position[0] + posX >= WIDTH_G or
                        self.piece.position[1] + posY < 0 or self.piece.position[1] + posY >= HEIGHT_G or
                        self.cells[self.piece.position[1] + posY][self.piece.position[0] + posX] != 0):
                    return False
                posX += 1
            posY += 1
        return True

    def movePart(self, NextP):
        if NextP == "D":
            self.piece.position = (self.piece.position[0], self.piece.position[1] - 1)
            if not self.checkMove():
                self.piece.position = (self.piece.position[0], self.piece.position[1] + 1)
                self.connectPart()
                return True  # switched piece
        if NextP == "R":
            self.piece.position = (self.piece.position[0] + 1, self.piece.position[1])
            if not self.checkMove():
                self.piece.position = (self.piece.position[0] - 1, self.piece.position[1])
        if NextP == "L":
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
                return True
            self.piece.rotation = temp
            self.piece.position = (self.piece.position[0] - 2, self.piece.position[1])
            self.piece.rotate()
            if self.checkMove():
                return True
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
        if self.solo:
            self.restart = True
        self.alive = False
        self.send("LostGame", "")

    def addLines(self, amount):
        current = sum(1 for row in self.cells if row != [0] * WIDTH_G)
        while amount > 0 and amount + current >= HEIGHT_G:
            amount -= 1
        if amount == 0:
            return False
        if self.piece.position[1] <= amount + current < HEIGHT_G:
            self.piece.position = (self.piece.position[0], self.piece.position[1] + amount)
        self.cells[amount:HEIGHT_G] = self.cells[:HEIGHT_G - amount]
        num = random.randint(0, WIDTH_G - 1)
        self.cells[:amount] = [[8 if c != num else 0 for c in range(WIDTH_G)] for _ in range(amount)]


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
        return 3, 17 if all_empty else 16


def restart(game):
    game.cells = [[0 for _ in range(WIDTH_G)] for _ in range(HEIGHT_G)]
    game.pieceLis = [0, 1, 2, 3, 4, 5, 6]
    game.holdPiece = None
    game.add_score(game.name, game.points)
    game.send("GetSeed", "")
    game.print_winners(game.places)
    game.places = None
    game.first_piece()
    game.send("UpdateGrid", game.crate_opp_cells())
    game.restart = False
    game.speed_time = 0.75
    game.points = 0


game = Game()
game.print_start()
game.first_piece()
game.printScreen()

start_time2 = time.time()
start_time = time.time()
start_timeR = time.time()
start_timeL = time.time()
start_timeD = time.time()
game.send("UpdateGrid", game.crate_opp_cells())

while True:
    if game.restart:
        restart(game)
    if game.alive:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_SPACE:
                    game.allDown()
                    game.checkAndRemoveRow()
                if event.key == pygame.K_LSHIFT:
                    game.hold()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and time.time() - start_timeR > 0.07:
            game.movePart("R")
            start_timeR = time.time()
        if keys[pygame.K_LEFT] and time.time() - start_timeL > 0.07:
            game.movePart("L")
            start_timeL = time.time()
        if keys[pygame.K_DOWN] and time.time() - start_timeD > 0.07:
            game.movePart("D")
            game.checkAndRemoveRow()
            start_timeD = time.time()
        if time.time() - start_time2 > 0.5:
            game.send("UpdateGrid", game.crate_opp_cells())
            start_time2 = time.time()
        current_time = time.time()
        if current_time - start_time >= game.speed_time:
            start_time = current_time
            game.movePart("D")
            game.checkAndRemoveRow()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    game.printScreen()
    pygame.display.flip()
    clock.tick(30)