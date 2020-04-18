import pygame
import math
import random
import time


keys = []
pg = pygame

pg.init()
pg.display.init()

screenwidth = 1920
screenheight = 1080

screen = pg.display.set_mode((screenwidth, screenheight))

carimg = pygame.transform.scale(pg.image.load("Car.png"), (128, 64))

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
        if posneg == 1:
            if cw:
                self.direction -= self.turnRad
                if self.direction < 0:
                    self.direction = (2 * math.pi)
            if ccw:
                self.direction += self.turnRad
                if self.direction > (2 * math.pi):
                    self.direction = 0
            self.x += math.cos(self.direction)
            self.y += math.sin(self.direction)
        if posneg == -1:
            if cw:
                self.direction += self.turnRad
                if self.direction > (2*math.pi):
                    self.direction = 0
            if ccw:
                self.direction -= self.turnRad
                if self.direction < 0:
                    self.direction = (2*math.pi)
            self.x -= math.cos(self.direction)
            self.y -= math.sin(self.direction)

    def draw(self):
        screen.blit(pg.transform.rotate(carimg, -(math.degrees(self.direction) - 180)), (self.x, self.y))
        #  pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height))
        pass

    def playerIn(self):
        self.hasPlayer = True

    def playerOut(self):
        self.hasPlayer = False




class Hitbox:

    def __init__(self, activex, activey, actwidth, actheight, passivex, passivey, paswidth, pasheight,
                 parent):
        self.activex = activex
        self.activey = activey
        self.actrightx = activex + actwidth
        self.actrighty = activey
        self.actdownx = activex
        self.actdowny = activey + actheight
        self.actfarx = activex + actwidth
        self.actfary = activey + actheight
        self.passivex = passivex
        self.passivey = passivey
        self.pasfarx = passivex + paswidth
        self.pasfary = passivey + pasheight
        self.parent = parent

    def hit(self):
        if (((self.activex > self.passivex and self.activex < self.pasfarx and
             self.activey > self.passivey and self.activey < self.pasfary)
            or (self.actrightx > self.passivex and self.actrightx < self.pasfarx and
                self.actrighty > self.passivey and self.actrighty < self.pasfary)
            or (self.actdownx > self.passivex and self.actdownx < self.pasfarx and
                self.actdowny > self.passivey and self.actdowny < self.pasfary)
            or (self.actfarx > self.passivex and self.actfarx < self.pasfarx and
                self.actfary > self.passivey and self.actfary < self.pasfary))) and self.parent.blit:
            return True
        else:
            return False

    def laserHit(self):
        if (self.activex > self.passivex and self.activex < self.pasfarx and
             self.activey > self.passivey and self.activey < self.pasfary) and self.parent.blit:
            return True
        else:
            return False

    def inside(self):
        if ((self.activex > self.passivex and self.activex < self.pasfarx and
             self.activey > self.passivey and self.activey < self.pasfary)
            and (self.actrightx > self.passivex and self.actrightx < self.pasfarx and
                self.actrighty > self.passivey and self.actrighty < self.pasfary)
            and (self.actdownx > self.passivex and self.actdownx < self.pasfarx and
                self.actdowny > self.passivey and self.actdowny < self.pasfary)
            and (self.actfarx > self.passivex and self.actfarx < self.pasfarx and
                self.actfary > self.passivey and self.actfary < self.pasfary)):
            return True
        else:
            return False

    def slope(self, y2, y1, x2, x1):
        return ((y2-y1)/(x2-x1))

    def linefunctionx(self, x, y, pointx, pointy):
        slope = self.slope(pointy, y, pointx, x)
        return (slope * (x - pointx)) + pointy

    def linefunctiony(self, x, y, pointx, pointy):
        slope = self.slope(pointy, y, pointx, x)
        return ((y - pointy) / slope) + pointx

    def bulletPrediction(self, x, y, speedx, speedy):
        newx = x + speedx

    #def laser(self, direction, x, y):
    #    slope = self.slope(math.sin(direction) + 10, y, math.cos(direction) + 10, x)
    #    y1 = self.linefunctionx(slope, self.passivex, self.activex, self.activey)
    #    y2 = self.linefunctionx(slope, self.pasfarx, self.activex, self.activey)
    #    x1 = self.linefunctiony(slope, self.passivey, self.activex, self.activey)
    #    x2 = self.linefunctiony(slope, self.pasfary, self.activex, self.activey)
    #    if ((y1 > self.passivey and y1 < self.pasfary) or (y2 > self.passivey and y2 < self.pasfary) or
    #        (x1 > self.passivex and x1 < self.pasfarx) or (x2 > self.passivex and x2 < self.pasfarx)):
    #        return True
    #    else:
    #        return False

    def getParent(self):
        return self.parent

    def changeActive(self, activex, activey):
        self.activex = activex
        self.activey = activey

    def changePassive(self, passivex, passivey):
        self.passivex = passivex
        self.passivey = passivey

zonewidth = 800
zoneheight = 800

class Zone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = None
        self.width = zonewidth
        self.height = zoneheight
        self.recbin = Hitbox(0, 0, 64, 64, (89*4) + x, (59*4) + y, (12*4), (8*4), player)
        self.garbin = Hitbox(0, 0, 64, 64, (89) + x, (75*4) + y, (13*4), (10*4), player)
        self.mailbox = Hitbox(0, 0, 64, 64, (85) + x, (5*4) + y, (12*4), (8*4), player)
        self.house = Hitbox(0, 0, 64, 64, (105) + x, (8*4) + y, (87*4), (91*4), player)
        self.door = Hitbox(0, 0, 64, 64, (103) + x, (16*4) + y, (18*4), (2*4), player)
        self.zonehitbox = Hitbox(0,0, 64, 64, x, y, zonewidth, zoneheight, player)
        self.recbincont = None
        self.garbincont = None
        self.mailboxcont = None

    def getMailbox(self):
        return self.mailboxcont
    def getRecbin(self):
        return self.recbincont
    def getGarbin(self):
        return self.garbincont

    def setContents(self, recbin, garbin, mailbox):
        self.recbincont = recbin
        self.garbincont = garbin
        self.mailboxcont = mailbox

class Map:
    def __init__(self, screenwidth, screenheight):
        self.sizew = 0
        while self.sizew < screenwidth:
            self.sizew += zonewidth
            if self.sizew > screenwidth:
                self.sizew += zonewidth
                self.mapwidth = self.sizew/zonewidth
        self.sizeh = 0
        while self.sizeh < screenheight:
            self.sizeh += zoneheight
            if self.sizeh > screenheight:
                self.sizeh += zoneheight
                self.mapheight = self.sizeh/zoneheight
        self.startingpointx = (screenwidth - zonewidth) / 2
        self.startingpointy = (screenheight - zoneheight) / 2
        self.zonesx = []
        self.zonesy = []
        self.zonediffx = self.startingpointx - (self.mapwidth/2)
        self.zonediffy = self.startingpointy - (self.mapheight/2)
        for zone in range(self.mapwidth):
            for zones in range(self.mapheight):
                self.zonesy.append(Zone(self.startingpointx + self.zonediffx, self.startingpointy + self.zonediffy))
                self.zonediffy += zoneheight
            self.zonesx.append(self.zonesy)
            self.zonediffy = 0
            self.zonesy.clear()
            self.zonediffx += zonewidth

    def setZone(self):
        if self.zonesx[(self.mapwidth/2)-1][(self.mapheight/2)-1].zonehitbox.hit():
            pass


tile_size = int(height / 15)
map = TileMap(1) #  (width / tile_size * 2)
car = Car((width/2), (height/2))
player = MainPlayer()

while run:
    screen.fill((255, 255, 255))

    pressedw = False
    presseda = False
    presseds = False
    pressedd = False
    posneg = 0
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
    if pressedw and not presseds:
        posneg = 1
    if not pressedw and presseds:
        posneg = -1
    if pressedd:
        ccw = True
    else:
        ccw = False
    if presseda:
        cw = True
    else:
        cw = False

    car.move(posneg, cw, ccw)
    car.draw()

    pg.display.update()