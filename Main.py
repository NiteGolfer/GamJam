import pygame
import math
import random
import time


keys = []
pg = pygame

pg.init()
pg.display.init()

screen = pg.display.set_mode((1920, 1080))

run = True
inputlatch = False
drawn_objects = []
dist = [0, 0]
height = 1080
width = 1920


class drawnObject:

    def __init__(self, cords=[0,0], layer=None):
        self.cords = cords
        global drawn_objects
        if layer == 0:
            drawn_objects.insert(layer, self)
        else:
            drawn_objects.insert(len(drawn_objects), self)

    def draw(self):
        pass


class Tile(drawnObject):

    def __init__(self, x, y, tile_size):
        super().__init__(layer=0)
        self.cords = [x, y]
        self.size = tile_size
        self.type = None
        self.chance = 15
        self.item = self.pickItem()

    def pickItem(self):
        return None

    def draw(self):
        pass

    def use(self):
        return "N"


class Road(Tile):

    def __init__(self, x, y, direction=0):
        super().__init__(x, y, tile_size)
        self.direction = direction
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def draw(self):
        return 
        pygame.draw.rect(screen, self.color,
                         (self.cords[0] - self.size / 2, self.cords[1]  - self.size / 2, self.size, self.size))
        pygame.draw.rect(screen, (0, 0, 0),
                         (self.cords[0] - self.size / 2, self.cords[1] - self.size / 2, self.size, self.size), 2)

    def use(self):
        self.color = (0, 0, 0)
        return "N"

    def pickItem(self):
        return None
        for item in items:
            if random.randint(0, 100) < self.chance:
                return item()



class TileMap:

    def __init__(self, size):
        self.tiles = []
        self.tile_size = tile_size
        r = int(size/2)
        self.tiles.append([Road(width / 2, height / 2, tile_size)])
        self.offscreen = 50
        while self.tiles[0][0].cords[0] >= -tile_size * self.offscreen / 2:
            self.build_left(e=True)
        while self.tiles[-1][-1].cords[0] <= width + tile_size* self.offscreen / 2:
            self.build_right(e=True)
        while self.tiles[0][0].cords[1] >= -tile_size * self.offscreen / 2:
            self.build_up(e=True)
        while self.tiles[-1][-1].cords[1] <= height + tile_size * self.offscreen / 2:
            self.build_down(e=True)

    def build_left(self, e=False):
        for index, row in  enumerate(self.tiles):
            row.insert(0, Road(row[0].cords[0] - self.tile_size, row[0].cords[1]))
            if not e:
                del row[-1]

    def build_right(self, e=False):
        for index, row in  enumerate(self.tiles):
            row.insert(len(row), Road(row[-1].cords[0] + self.tile_size, row[-1].cords[1]))
            if not e:
                del row[0]

    def build_up(self, e=False):
        new_row = []
        for tile in self.tiles[0]:
            new_row.append(Road(tile.cords[0], tile.cords[1] - self.tile_size))
        if not e:
            del self.tiles[-1]
        self.tiles.insert(0, new_row)

    def build_down(self, e=False):
        new_row = []
        for tile in self.tiles[-1]:
            new_row.append(Road(tile.cords[0], tile.cords[1] + self.tile_size))
        if not e:
            del self.tiles[0]
        self.tiles.insert(len(self.tiles), new_row)

    def print(self):
        string = ""
        for row in self.tiles:
            new_row = ""
            for tile in row:
                new_row += str(tile.cords[0]) + ":" + str(tile.cords[1]) + " "
            string += new_row + "\n"
        print(string)


class Player(drawnObject):

    def __init__(self, cords):
        super().__init__()
        self.cords = cords
        self.speed = 20
        self.index = 0
        self.max_health = 100
        self.health = self.max_health
        self.skin = pg.transform.smoothscale(pg.image.load('Player1-1.png'), (64, 64))
        self.delta = [0, 0]
        self.size = 64
        self.dead = False
        self.bullets = []
        self.angle = 0
        self.find_angle()

    def find_angle(self):
        pos = pg.mouse.get_pos()
        x = pos[0] - width / 2
        y = pos[1] - height / 2
        angle = math.atan2(y, x)
        angle = (180 / math.pi) * (-angle) - 90
        self.angle = angle

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.dead = True

    def draw(self):
        r = (width / 2 - self.size / 2, height / 2 - self.size / 2, self.size, self.size)
        self.find_angle()
        screen.blit(pygame.transform.rotozoom(self.skin, self.angle, 1), r)


class MainPlayer(Player):

    def __init__(self):
        super().__init__(cords=[width / 2, height / 2])
        self.delay = 0.2
        self.lastShot = -self.delay

    def move(self, delta=[0, 0]):
        self.delta = [0, 0]
        if delta != [0, 0]:
            self.delta = delta
        for key in keys:
            self.handleKeyDown(key)
        tiles = map.tiles
        # Handle X cords
        cords = tiles[0][0].cords
        if cords[0] - self.delta[0] > -tile_size * map.offscreen / 2:
            map.build_left()
            dist[0] -= 1
        cords = tiles[-1][-1].cords
        if cords[0] - self.delta[0] < width + tile_size * map.offscreen / 2:
            map.build_right()
            dist[0] += 1

        # Handle Y cords
        cords = tiles[0][0].cords
        if cords[1] - self.delta[1] > -tile_size * map.offscreen / 2:
            map.build_up()
            dist[1] -= 1
        cords = tiles[-1][-1].cords
        if cords[1] - self.delta[1] < height + tile_size * map.offscreen / 2:
            map.build_down()
            dist[1] += 1

        global drawn_objects
        for object in drawn_objects:
            object.cords = [object.cords[0] - self.delta[0], object.cords[1] - self.delta[1]]

        '''
        cords = tiles[0][0].cords
        cords = [cords[0] + (width / 2 - self.cords[0]), cords[1] + (height / 2 - self.cords[1])]
        row = int(cords[0] / tile_size * -1 + width / tile_size / 2)
        col = int(cords[1] / tile_size * -1 + height / tile_size / 2)

        with open("C:\\Users\\Sean\\PycharmProjects\\2dTile\\Updates", 'w') as f:
            f.write(baseURL + "Players/Update/" + str(row) + "/" + str(col) + "/" + str(playerIndex))
        '''

    def handleKeyDown(self, key):
        key = chr(key)
        if key == 'w':
            self.delta[1] = -self.speed
        if key == 's':
            self.delta[1] = self.speed
        if key == 'a':
            self.delta[0] = -self.speed
        if key == 'd':
            self.delta[0] = self.speed
        if key == ' ':
            self.shoot()

    def shoot(self):
        if time.time() - self.lastShot < self.delay:
            return
        self.lastShot = time.time()
        xy = pg.mouse.get_pos()
        a = self.angle
        s = math.sin(math.radians(a))
        c = math.cos(math.radians(a))
        self.bullets.append(Bullet([width / 2 + 2 * s, height / 2 - 7 * c], xy))

    def useTile(self):
        tiles = map.tiles
        cords = tiles[0][0].cords
        cords = [cords[0] + (width / 2 - self.cords[0]), cords[1] + (height / 2 - self.cords[1])]
        row = int(cords[0] / tile_size * -1 + width / tile_size / 2)
        col = int(cords[1] / tile_size * -1 + height / tile_size / 2)
        print(int(len(tiles) / 2.000001 + dist[1]), int(len(tiles[0]) / 2.000000001 + dist[0]))
        output = tiles[int(len(tiles) / 2.000001)][int(len(tiles[0]) / 2.000000001)].use()
        if output[-1] == "H":
            self.health += eval(output[:-1])
            if self.health > self.max_health:
                 self.health = 100

    def drawGUI(self):
        pygame.draw.rect((width / 10, height / 10 * 9, width / 10 * 8, height / 5))


class Bullet(drawnObject):

    def __init__(self, coming, going, speed=1, size=5):
        super().__init__(cords=coming)
        self.speed = speed
        self.cords = coming.copy()
        self.size = size
        self.delta = [going[0] - coming[0], going[1] - coming[1]]
        ratio = (self.delta[0] ** 2 + self.delta[1] ** 2) ** 0.5 / 25
        self.delta = [self.delta[0] * self.speed / ratio, self.delta[1] * self.speed / ratio]

    def draw(self):
        self.cords = [self.cords[0] + self.delta[0], self.cords[1] + self.delta[1]]
        pygame.draw.circle(screen, (255, 255, 255), [int(self.cords[0]), int(self.cords[1])], self.size)


class Car(drawnObject):

    def __init__(self, x, y):
        super().__init__(cords=[x,y])
        self.x = x
        self.y = y
        self.width = 100
        self.height = 25
        self.img = None
        self.hasPlayer = True
        self.turnRad = 0.01
        self.direction = 0

    def move(self, posneg, cw, ccw):
        if cw:
            self.direction -= self.turnRad
            if self.direction < 0:
                self.direction = (2*math.pi)
        if ccw:
            self.direction += self.turnRad
            if self.direction > (2*math.pi):
                self.direction = 0
        if posneg:
            self.x += math.cos(self.direction)
            self.y += math.sin(self.direction)
        if not posneg:
            self.x += math.cos(self.direction)
            self.y += math.sin(self.direction)

    def draw(self):
        #  pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height))
        pass

    def playerIn(self):
        self.hasPlayer = True

    def playerOut(self):
        self.hasPlayer = False


tile_size = int(height / 15)
map = TileMap(1) #  (width / tile_size * 2)
car = Car((width/2), (height/2))
player = MainPlayer()

while run:
    screen.fill((0, 0, 0))
    # getting input
    for event in pygame.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit(0)
        if event.type == pg.MOUSEBUTTONDOWN:
            inputlatch = True
        if event.type == pg.MOUSEBUTTONUP:
            inputlatch = False
        if event.type == pg.KEYDOWN:
            keys.append(event.key)
        if event.type == pg.KEYUP:
            try:
                keys.remove(event.key)
            except ValueError:
                pass
    if pg.mouse.get_pressed()[0]:
        fireanimchange = True
    player.move()
    #getting keyed input
    keycheck = pg.key.get_pressed()

    for object in drawn_objects:
        object.draw()

    if keycheck[pg.K_w]:
        pressedw = True
    if keycheck[pg.K_a]:
        presseda = True
    if keycheck[pg.K_s]:
        presseds = True
    if keycheck[pg.K_d]:
        pressedd = True

    pg.display.update()



