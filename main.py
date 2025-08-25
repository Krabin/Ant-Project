from collections import deque

import pygame
import random
import math
import numpy as np
import sys
from pygame.locals import *

# constants
FPS=30


##Constant screensize
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

##Constant Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

##Anthill constants
# Anthill position -> Center of screen
ANTHILL_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
ANTHILL_COLOR = GREEN
ANTHILL_SIZE = 20

##Ant Constants
ANT_SPEED = 1
NUM_ANTS = 100
PHEROMONE_DETECTION_RANGE = 100
FOOD_DETECTION_RANGE = 100
FOOD_COLLECTION_RANGE = 10
PHEROMONE_SPAWN_COOLDOWN = 10
DIRECTION_CHANGE_COOLDOWN = 10

##pheromone constants
PHEROMONE_PERCENT_DECAY_RATE = .999
PHEROMONE_FLAT_DECAY_RATE = .01
PHEROMONE_STARTING_STRENGTH = 255
PHEROMONE_GRID_SIZE = (20, 20)
PHEROMONE_GRID_WIDTH = SCREEN_WIDTH//20
PHEROMONE_GRID_HEIGHT = SCREEN_HEIGHT//20
PHEROMONE_ZONE_SEARCH_RADIUS = 1


class FoodManager():
    def __init__(self):
        # Set food position to upper left corner just to test things
        self.xpos = SCREEN_WIDTH // 4
        self.ypos = SCREEN_HEIGHT // 4

    def getfoodposition(self):
        return (self.xpos, self.ypos)

    def getdistancefromfood(self, xpos, ypos):
        # Calculates flat distance between two points
        return math.sqrt((xpos - self.xpos) ** 2 + (ypos - self.ypos) ** 2)

    def drawfood(self, surface):
        pygame.draw.circle(surface, RED, (self.xpos, self.ypos), 1)


class PheromoneManager():
    def __init__(self, color):
        # Initalize a grid of 20x20 chunks to contain pharamones
        self.color = color
        self.pheromone_zones = np.empty(PHEROMONE_GRID_SIZE, dtype=object)
        # Each chunk represents 1/20th of the screen size in any direction. With chunk [0,0] represenitng the grid starting at [0,0] to [SCREEN_WIDTH/20,SCREENHEIGHT/20]
        # Initalize an empty list into each item on the chunk.
        for i in range(PHEROMONE_GRID_SIZE[0]):
            for j in range(PHEROMONE_GRID_SIZE[1]):
                self.pheromone_zones[i, j] = []

    def update(self):
        for i in range(PHEROMONE_GRID_SIZE[0]):
            for j in range(PHEROMONE_GRID_SIZE[1]):
                updated_list = []
                for k in self.pheromone_zones[i, j]:
                    k.update()
                    if k.strength > 0:
                        updated_list.append(k)
                self.pheromone_zones[i, j] = updated_list

    def addpheromone(self, xpos, ypos):
        x_zone = int(xpos // PHEROMONE_GRID_WIDTH)
        y_zone = int(ypos // PHEROMONE_GRID_HEIGHT)
        new_phera = Pheromone(xpos, ypos, self.color)
        if x_zone >= 20:
            print(x_zone)
        if y_zone >= 20:
            print(y_zone)
        self.pheromone_zones[x_zone, y_zone].append(new_phera)

    def getnearbypharamones(self, xpos, ypos):
        x_zone = int(xpos // PHEROMONE_GRID_WIDTH)
        y_zone = int(ypos // PHEROMONE_GRID_HEIGHT)

        x_lower = max(0,x_zone-1)
        x_upper = min(19,x_zone+1)

        y_lower = max(0,y_zone-1)
        y_upper = min(19,x_zone+1)



        nearby_pheromones = []
        if x_upper >= 20:
            print(x_upper)
        if y_upper >= 20:
            print(y_upper)

        for x in range(x_lower, x_upper+1):
            for y in range(y_lower, y_upper+1):
                nearby_pheromones += self.pheromone_zones[x,y]

        return nearby_pheromones


    def draw(self, surface):
        for i in range(PHEROMONE_GRID_SIZE[0]):
            for j in range(PHEROMONE_GRID_SIZE[1]):
                for k in self.pheromone_zones[i, j]:
                    k.draw(surface)

class Pheromone:
    def __init__(self, xpos, ypos, color):
        self.xpos = xpos
        self.ypos = ypos
        self.strength = PHEROMONE_STARTING_STRENGTH
        self.color = color

    def update(self):
        self.strength = ((self.strength - PHEROMONE_FLAT_DECAY_RATE) * PHEROMONE_PERCENT_DECAY_RATE)
        # if the pheramone strength is less than zero, return true and signal this to object to be deleted
        if self.strength <= 0:
            return True
        else:
            return False

    def draw(self, surface):

        colorstrength = tuple(map(lambda x: int((x/255) * self.strength), self.color))
        pygame.draw.circle(surface, colorstrength, (self.xpos, self.ypos), 3)

class Ant:
    def __init__(self, xpos, ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.speed = ANT_SPEED
        self.direction = random.uniform(0, 2*math.pi)
        self.has_food = False
        self.food_target = None
        self.direction_change_cooldown = DIRECTION_CHANGE_COOLDOWN
        self.pheromone_cooldown = PHEROMONE_SPAWN_COOLDOWN

    def move(self):
        #Temp random movement for proof of concept

        #pathfinding for having food
        if self.has_food == True:
            if distance((self.xpos,self.ypos),(ANTHILL_POSITION)) < 20:
                self.has_food = False
                self.food_target = None


            #else:
                #Drop HaveFood pheramone
                #compte average pheramone direction
        #else:
            #if ant is near food
                #go towards food get food
            #else




        #if it is time for a direction change
        if self.direction_change_cooldown == 0:
            #rotate by .2 radians
            self.direction = self.direction+random.uniform(-.2 , .2)
            #reset direction cooldown timer
            self.direction_change_cooldown = DIRECTION_CHANGE_COOLDOWN


        #do movement
        self.xpos += self.speed * math.cos(self.direction)
        self.ypos += self.speed * math.sin(self.direction)

        #bound movement to screen flip direction if outside
        if self.xpos <= 0 or self.xpos >= SCREEN_WIDTH:
            self.xpos = 1 if self.xpos <= 0 else SCREEN_WIDTH - 1
            self.direction = math.atan2(math.sin(self.direction), -math.cos(self.direction))

        if self.ypos <= 0 or self.ypos >= SCREEN_HEIGHT:
            self.ypos = 1 if self.ypos <= 0 else SCREEN_HEIGHT - 1
            self.direction = math.atan2( -math.sin(self.direction),  math.cos(self.direction))

        if self.direction <= 0:
            self.direction = self.direction + math.pi*2

        if self.direction >= math.pi*2:
            self.direction = self.direction - math.pi*2



        if self.pheromone_cooldown <= 0:
            self.pheromone_cooldown = PHEROMONE_SPAWN_COOLDOWN
            home_pheromones.addpheromone(self.xpos, self.ypos)

        self.pheromone_cooldown = self.pheromone_cooldown-1


        #reduce count on direction change cooldown
        self.direction_change_cooldown = self.direction_change_cooldown-1



        #Return food and go searching again

        #Check if you have food
            #if no food
                #bias movement towards weighted average position of all nearby food pharamones
                #if no food pheramones

    def direction_to(self,xpos,ypos):
        return math.atan2(ypos - self.ypos, xpos - self.xpos)

    def draw(self, surface):
        color = GREEN
        pygame.draw.circle(surface, color, (int(self.xpos), int(self.ypos)), 3)

def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

#pygame init
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(BLACK)
FramePerSec = pygame.time.Clock()
ants = [Ant(ANTHILL_POSITION[0], ANTHILL_POSITION[1]) for _ in range(NUM_ANTS)]

food = FoodManager()

home_pheromones = PheromoneManager(BLUE)
food_pheromones = PheromoneManager(RED)



while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)

    #update pharamones
    home_pheromones.update()
    home_pheromones.draw(screen)

    food_pheromones.update()
    food_pheromones.draw(screen)
    #drraw anthill
    pygame.draw.circle(screen, ANTHILL_COLOR, ANTHILL_POSITION, ANTHILL_SIZE)

    #update ants
    for ant in ants:
        ant.move()
        ant.draw(screen)

    temp = home_pheromones.getnearbypharamones(ants[0].xpos,ants[0].ypos)
    #draw pheromones

    #draw ants

    #draw food
    food.drawfood(screen)

    #Draw anthill


    pygame.display.flip()
    FramePerSec.tick(FPS)