import math
import random
import time
import pygame

drawn_objects = []
keys = []
height = screen.height
tile_size = int(height / 22)
map = TileMap(100, int(height / 22))

class drawnObject:

    def __init__(self):
        self.cord = [0, 0]
        global drawn_objects
        drawn_objects.append(self)

    def draw(self):
        pass


class Tile(drawnObject):

    def __init__(self, x, y, tile_size):
        super().__init__()
        self.cords = [x, y]
        self.size = tile_size
        self.type = None

    def draw(self):
        pass

    def use(self):
        return ""


class Road(Tile):

    def __init__(self, x, y, tile_size, direction):
        super().__init__(x, y, tile_size)
        self.direction = direction

    def draw(self):
        pass

class TileMap:

    def __int__(self, size, tile_size):
        self.tiles = []
        self.tile_size = tile_size
        for x in range(size/-2, size/2):
            new_row = []
            for i in range(size/-2, size/2):
                new_row.append(Tile(x * tile_size, y * tile_size), tile_size)

    def build_left(self):
        for index, row in  enumerate(self.tiles):
            row.insert(0, Tile(row[0].cords[0] - self.tile_size, row[0].cords[1]))
            row.remove(len(row) - 1)

    def build_right(self):
        for index, row in  self.tiles:
            row.insert(len(row), Tile(row[0].cords[0] - self.tile_size, row[0].cords[1]))
            row.remove(0)

    def build_up(self):
        new_row = []
        for tile in self.tiles[0]:
            new_row.append(Tile(tile.cords[0], tile.cords[1] - self.tile_size), tile_size)
        self.tiles.insert(0, new_row)
        del self.tiles[-1]

    def build_down(self):
        new_row = []
        for tile in self.tiles[-1]:
            new_row.append(Tile(tile.cords[0], tile.cords[1] - self.tile_size), tile_size)
        self.tiles.insert(len(self.tiles), new_row)
        del self.tiles[-1]


class Player(drawnObject):

    def __init__(self, cords):
        super().__init__()
        self.cords = cords
        self.speed = 20
        self.index = 0
        self.max_health = 100
        self.health = self.max_health
        self.delta = [0, 0]
        self.dead = False

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.dead = True

    def draw(self):
        #TODO draw player
        pass


class MainPlayer(Player):

    def __init__(self):
        super().__init__(cords=[width / 2, height / 2])

    def move(self, dt, delta=[0, 0]):
        self.delta = [0, 0]
        if delta != [0, 0]:
            self.delta = delta
        for key in keys:
            self.handleKeyDown(key)

        # Handle X cords
        if (self.cords[0] > width / 2 and self.delta[0] < 0):
            self.cords[0] += self.delta[0]
            self.delta[0] = 0
            if self.cords[0] < width / 2:
                self.delta[0] = 0
                self.cords[0] = width / 2
        if (self.cords[0] < width / 2 and self.delta[0] > 0):
            self.cords[0] += self.delta[0]
            self.delta[0] = 0
            if self.cords[0] > width / 2:
                self.delta[0] = 0
                self.cords[0] = width / 2

        cords = tiles[0][0].cords
        if cords[0] - self.delta[0] > 0:
            self.cords[0] += self.delta[0]
            self.delta[0] = 0
            if self.cords[0] < 1:
                self.cords[0] = 1
                self.delta[0] = 0
        cords = tiles[99][99].cords
        if cords[0] - self.delta[0] < width - tile_size:
            self.cords[0] += self.delta[0]
            self.delta[0] = 0
            if self.cords[0] > width - 20:
                self.cords[0] = width - 20
                self.delta[0] = 0

        # Handle Y cords
        if (self.cords[1] > height / 2 and self.delta[1] < 0):
            self.cords[1] += self.delta[1]
            self.delta[1] = 0
            if self.cords[1] < height / 2:
                self.delta[1] = 0
                self.cords[1] = height / 2
        if (self.cords[1] < height / 2 and self.delta[1] > 0):
            self.cords[1] += self.delta[1]
            self.delta[1] = 0
            if self.cords[1] > height / 2:
                self.delta[1] = 0
                self.cords[1] = height / 2

        cords = tiles[0][0].cords
        if cords[1] - self.delta[1] > 0:
            self.cords[1] += self.delta[1]
            self.delta[1] = 0
            if self.cords[1] < 1:
                self.cords[1] = 1
                self.delta[1] = 0
        cords = tiles[99][99].cords
        if cords[1] - self.delta[1] < height - tile_size:
            self.cords[1] += self.delta[1]
            self.delta[1] = 0
            if self.cords[1] > height - 94:
                self.cords[1] = height - 94
                self.delta[1] = 0

        for object in objects:
            object.cords = [object.cords[0] - self.delta[0], object.cords[1] - self.delta[1]]

        cords = tiles[0][0].cords
        cords = [cords[0] + (width / 2 - self.cords[0]), cords[1] + (height / 2 - self.cords[1])]
        row = int(cords[0] / tile_size * -1 + width / tile_size / 2)
        col = int(cords[1] / tile_size * -1 + height / tile_size / 2)

        # Save for later
        #  with open("C:\\Users\\Sean\\PycharmProjects\\2dTile\\Updates", 'w') as f:
        #      f.write(baseURL + "Players/Update/" + str(row) + "/" + str(col) + "/" + str(playerIndex))

    def handleKeyDown(self, key):
        if key == 'w':
            self.delta[1] = self.speed
        if key == 's':
            self.delta[1] = -self.speed
        if key == 'a':
            self.delta[0] = -self.speed
        if key == 'd':
            self.delta[0] = self.speed

    def useTile(self, dt):
        if not (" " in keys):
            return
        cords = tiles[0][0].cords
        cords = [cords[0] + (width / 2 - self.cords[0]), cords[1] + (height / 2 - self.cords[1])]
        row = int(cords[0] / tile_size * -1 + width / tile_size / 2)
        col = int(cords[1] / tile_size * -1 + height / tile_size / 2)
        output = tiles[row][col].use()
        if output[-1] == "H":
            self.health += eval(output[:-1])
            if self.health > self.max_health:
                 self.health = 100

    def drawGUI(self):
        #TODO create GUI
        pass