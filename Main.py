import pygame
import math
import random


pg = pygame

pg.init()
pg.display.init()

screenwidth = 1920
screenheight = 1080

screen = pg.display.set_mode((screenwidth, screenheight))

carimg = pygame.transform.scale(pg.image.load("Car.png"), (128, 64))

run = True
inputlatch = False

class Car:
    def __init__(self, x, y):
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

    def playerIn(self):
        self.hasPlayer = True

    def playerOut(self):
        self.hasPlayer = False

car = Car((screenwidth/2), (screenheight/2))

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


while run:

    screen.fill((255, 255, 255))

    pressedw = False
    presseda = False
    presseds = False
    pressedd = False
    posneg = 0

    # getting input
    for event in pygame.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            inputlatch = True
        if event.type == pg.MOUSEBUTTONUP:
            inputlatch = False

    if pg.mouse.get_pressed()[0]:
        fireanimchange = True

    #getting keyed input
    keycheck = pg.key.get_pressed()

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