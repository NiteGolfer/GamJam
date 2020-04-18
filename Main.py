import pygame
import math
import random


pg = pygame

pg.init()
pg.display.init()

screen = pg.display.set_mode((1920, 1080))

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
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.witch, self.height))

    def playerIn(self):
        self.hasPlayer = True

    def playerOut(self):
        self.hasPlayer = False

car = Car((screen.Width/2), (screen.height/2))

while run:

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



