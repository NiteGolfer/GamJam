import pygame
import math
import random
import time


keys = []
pg = pygame

pg.init()
pg.display.init()
pg.mixer.init()
font = pygame.font.Font('freesansbold.ttf', 30)
channels = [pg.mixer.Channel(0), pg.mixer.Channel(1), pg.mixer.Channel(2)]
clock = pygame.time.Clock()
song = pg.mixer.Sound('music.wav')
pew = pg.mixer.Sound('pew.mp3.wav')
vroom = pg.mixer.Sound('car_sound.wav')
channels[0].set_volume(1)

screenwidth = 1920
screenheight = 1080

pygame.font.init()

font = pg.font.Font("arial.ttf", 18)

screen = pg.display.set_mode((screenwidth, screenheight))

carimg = pygame.transform.scale(pg.image.load("Car.png"), (128, 64))
tileimg= pygame.transform.scale(pg.image.load("BG.png"), (800, 800))

run = True
inputlatch = False
drawn_objects = []
zombies = []
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


class Player(drawnObject):

    def __init__(self, cords):
        super().__init__()
        self.cords = cords
        self.speed = 1.5
        self.index = 0
        self.max_health = 1
        self.health = self.max_health
        self.skin = pg.transform.scale(pg.image.load('Player1.png'), (64, 64))
        self.delta = [0, 0]
        self.size = 64
        self.dead = False
        self.bullets = []
        self.angle = self.find_angle()

    def find_angle(self, other=None):
        if not other:
            pos = pg.mouse.get_pos()
            x = pos[0] - width / 2
            y = pos[1] - height / 2
        else:
            pos = other
            x = self.cords[0] - pos[0]
            y = self.cords[1] - pos[1]
        angle = math.atan2(y, x)
        angle = (180 / math.pi) * (-angle) - 90
        return angle

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.dead = True


class Zombie(Player):

    def __init__(self):
        super().__init__(cords=[0, 0])
        self.delay = 2
        self.lastHit = -self.delay
        zombies.append(self)

    def move(self):
        dist = ((width / 2 - self.cords[0]) ** 2 + (height / 2 - self.cords[1]) ** 2) ** 0.5
        Y = 90 - self.find_angle([width / 2, height / 2])
        X = 90 - Y
        self.angle = X
        if dist > 200:
            self.cords = [self.cords[0] - math.sin(X) * self.speed, self.cords[1] - math.sin(Y) * self.speed]

    def draw(self):
        r = (self.cords[0] - self.size / 2, self.cords[1] - self.size / 2, self.size, self.size)
        screen.blit(pygame.transform.rotozoom(self.skin, self.angle + 180, 1), r)


class MainPlayer(Player):

    def __init__(self):
        super().__init__(cords=[width / 2, height / 2])
        self.skin = pg.transform.scale(pg.image.load('Player1.png'), (64, 64))
        self.max_health = 100
        self.health = self.max_health
        self.delay = pew.get_length()
        self.lastShot = -self.delay
        self.reload_start = self.lastShot
        self.max_ammo = 100
        self.mag_size = 11
        self.mag = self.mag_size
        self.reload = 5
        self.ammo = self.max_ammo
        self.reloading = False
        self.inCar = False

    def draw(self):
        if self.inCar:
            if not channels[2].get_busy():
                channels[2].play(vroom)
            return
        #  r = (self.cords[0] - self.size / 2, self.cords[1] - self.size / 2, self.size, self.size)
        r = (width / 2 - self.size / 2, height / 2 - self.size / 2, self.size, self.size)
        self.angle = self.find_angle()
        screen.blit(pygame.transform.rotozoom(self.skin, self.angle, 1), r)

    def move(self, delta=[0, 0]):
        self.delta = [0, 0]
        if delta != [0, 0]:
            self.delta = delta
        for key in keys:
            self.handleKeyDown(key)
        global drawn_objects
        for object in drawn_objects:
            object.cords = [object.cords[0] - self.delta[0], object.cords[1] - self.delta[1]]
            try:
                object.x -= self.delta[0]
                object.y -= self.delta[1]
            except AttributeError:
                pass

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
        if key == 'r' and self.mag != self.mag_size:
            self.reload_start = time.time()
            self.reloading = True

    def shoot(self):
        if time.time() - self.lastShot < self.delay:
            return
        if time.time() - self.reload_start >= self.delay and self.reloading:
            self.reloading = False
            self.mag = self.mag_size

        if self.mag == 0:
            return

        self.mag -= 1
        self.ammo -= 1
        self.lastShot = time.time()
        xy = pg.mouse.get_pos()
        a = self.angle
        s = math.sin(math.radians(a))
        c = math.cos(math.radians(a))
        self.bullets.append(Bullet([width / 2 + 2 * s, height / 2 - 7 * c], xy))
        if not channels[1].get_busy():
            channels[1].play(pew)

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


class Bullet(drawnObject):

    def __init__(self, coming, going, speed=1, size=7):
        super().__init__(cords=coming)
        self.speed = speed
        self.cords = coming.copy()
        self.size = size
        self.range = 1000
        self.delta = [going[0] - coming[0], going[1] - coming[1]]
        ratio = (self.delta[0] ** 2 + self.delta[1] ** 2) ** 0.5 / 25
        self.delta = [self.delta[0] * self.speed / ratio, self.delta[1] * self.speed / ratio]

    def draw(self):
        self.cords = [self.cords[0] + self.delta[0], self.cords[1] + self.delta[1]]
        if ((player.cords[0] - self.cords[0]) ** 2 + (player.cords[1] - self.cords[1]) ** 2) ** 0.5 > self.range:
            drawn_objects.remove(self)
        pygame.draw.circle(screen, (75, 75, 75), [int(self.cords[0]), int(self.cords[1])], self.size)


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
                self.actfary > self.passivey and self.actfary < self.pasfary))):
            return True
        else:
            return False

    def bulletHit(self):
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

class Zone(drawnObject):
    def __init__(self, x, y):
        super().__init__(cords=[x,y])
        self.x = x
        self.y = y
        self.img = None
        self.width = zonewidth
        self.height = zoneheight
        self.recbin = Hitbox(0, 0, 64, 64, (89 * 4) + x, (59 * 4) + y, (12 * 4), (8 * 4), player)
        self.garbin = Hitbox(0, 0, 64, 64, (89) + x, (75 * 4) + y, (13 * 4), (10 * 4), player)
        self.mailbox = Hitbox(0, 0, 64, 64, (85) + x, (5 * 4) + y, (12 * 4), (8 * 4), player)
        self.house = Hitbox(0, 0, 64, 64, (105) + x, (8 * 4) + y, (87 * 4), (91 * 4), player)
        self.door = Hitbox(0, 0, 64, 64, (103) + x, (16 * 4) + y, (18 * 4), (2 * 4), player)
        self.zonehitbox = Hitbox(0, 0, 64, 64, x, y, zonewidth, zoneheight, player)
        self.recbincont = None
        self.garbincont = None
        self.mailboxcont = None

    def getMailbox(self):
        return self.mailboxcont

    def getRecbin(self):
        return self.recbincont

    def getGarbin(self):
        return self.garbincont

    def setHitboxes(self):
        self.recbin.changeActive(player.cords[0], player.cords[1])
        self.garbin.changeActive(player.cords[0], player.cords[1])
        self.mailbox.changeActive(player.cords[0], player.cords[1])
        self.house.changeActive(player.cords[0], player.cords[1])
        self.zonehitbox.changeActive(player.cords[0], player.cords[1])
        self.recbin.changePassive(self.x, self.y)
        self.garbin.changePassive(self.x, self.y)
        self.mailbox.changePassive(self.x, self.y)
        self.house.changePassive(self.x, self.y)
        self.zonehitbox.changePassive(self.x, self.y)

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
            self.mapwidth = self.sizew // zonewidth
        self.sizeh = 0
        while self.sizeh < screenheight:
            self.sizeh += zoneheight
            if self.sizeh > screenheight:
                self.sizeh += zoneheight
                self.mapheight = self.sizeh // zoneheight
        self.startingpointx = (screenwidth - zonewidth) / 2
        self.startingpointy = (screenheight - zoneheight) / 2
        self.zonesx = []
        self.zonesy = []
        self.zonediffx = self.startingpointx - (self.sizew / 2)
        self.zonediffy = self.startingpointy - (self.sizeh / 2)
        for zone in range(self.mapwidth):
            self.zonesx.append([])
            for zones in range(self.mapheight):
                self.zonesx[zone].append(Zone(self.startingpointx + self.zonediffx, self.startingpointy + self.zonediffy))
                self.zonediffy += zoneheight
            self.zonediffy = self.startingpointy - (self.sizeh / 2)
            self.zonediffx += zonewidth

    def setZone(self):
        self.zonesx[(self.mapwidth // 2)][(self.mapheight // 2)].zonehitbox.changeActive(player.cords[0],
                                                                                               player.cords[1])
        if not self.zonesx[(self.mapwidth // 2)][(self.mapheight // 2)].zonehitbox.hit():
            print("uh oh")
            for zones in self.zonesx:
                for zone in zones:
                    if zone.zonehitbox.hit():
                        if zones.index(zone) < self.mapheight/2:
                            pass
                        if zones.index(zone) > self.mapheight/2:
                            pass
                        if self.zonesx.index(zones) < self.mapwidth/2:
                            print(self.zonesx.index(zones), self.mapwidth/2)
                            self.zonesx.remove(self.zonesx[len(self.zonesx) - 1])
                            self.zonesx.insert(0, [])
                            for zone in range(self.mapheight):
                                self.zonesx[0].append(Zone(self.zonesx[1][zone].x - zonewidth,
                                                      self.zonesx[1][zone].y))
                        if self.zonesx.index(zones) > self.mapwidth/2:
                            self.zonesx.remove(0)
                            self.zonesx.append([])
                            for zone in range(self.mapheight):
                                self.zonesx[len(self.zonesx) - 1].append(Zone(self.zonesx[len(self.zonesx) - 2][zone].x - zonewidth,
                                                                         self.zonesx[len(self.zonesx) - 2][zone].y))

    def draw(self):
        for zones in self.zonesx:
            for zone in zones:
                screen.blit(tileimg, (zone.cords[0], zone.cords[1]))


car = Car((width/2), (height/2))
player = MainPlayer()
Zombie()
ubermap = Map(screenwidth, screenheight)


def drawGUI():
    pygame.draw.rect(screen, (0, 0, 0), (width / 10, height / 10 * 9, width / 10 * 8, height / 20))
    pygame.draw.rect(screen, (200, 75, 75),
                     (width / 10, height / 10 * 9, width / 10 * 8 * player.health / player.max_health, height / 20))
    if player.mag / player.mag_size < 0.1:
        string = "Low Ammo!!!"
        text = pygame.font.Font.render(font, string, True, (255, 50, 50))
        screen.blit(text, (width / 2 - font.size(string)[0] / 2, height / 9 * 7.5 + - font.size(string)[1] / 2))


class Button:

    def __init__(self, x, y, active, inactive, font, text):
        self.screen = screen
        self.x = x
        self.y = y
        self.hitbox = Hitbox(0, 0, 0, 0, x, y, 256, 64, None)
        self.active = active
        self.inactive = inactive
        self.blit = True
        self.font = font
        self.text = text

    def button(self):

        if self.hitbox.hit():
            self.screen.blit(self.active, (self.x, self.y))
        else:
            self.screen.blit(self.inactive, (self.x, self.y))
        self.screen.blit(self.font.render(self.text, True, (255, 255, 255)), (self.x, self.y))

startimg2 = pg.transform.scale(pg.image.load("Menus1.png"), (256, 64))
startimg1 = pg.transform.scale(pg.image.load("Menus2.png"), (256, 64))

startbutton = Button(0, 0, startimg1, startimg2, font, "Start!")

start = True
while run:

    while start:
        startbutton.hitbox.changeActive(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])
        pg.event.get()
        screen.fill((255, 255, 255))
        startbutton.button()
        pygame.display.update()
        if startbutton.hitbox.hit() and pg.mouse.get_pressed()[0]:
            start = False

    for zones in ubermap.zonesx:
        for zone in zones:
            zone.setHitboxes()

    if not channels[0].get_busy():
        channels[0].play(song)
    screen.fill((255, 255, 255))
    ubermap.setZone()
    ubermap.draw()

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
    for zombie in zombies:
        zombie.move()
    player.move()
    if pg.mouse.get_pressed()[0] == 1:
        player.shoot()
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
    drawGUI()
    pg.display.update()
    clock.tick(60)