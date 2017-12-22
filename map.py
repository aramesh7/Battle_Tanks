import pygame
import math
import random
from Tanks import utils


'''
This class handles the mutable terrain in the game.
There are 3 types of terrain

- Snow
- Hill
- Desert
- Moon
'''

class Map:
    def __init__(self,screen, type, screen_dims):
        random.seed()
        self.screen = screen
        self.maps = {
            "Snow": {'terrain': self.snow_terrain, 'background': 'images/snow_bg.jpg', 'color': (255, 250, 250)},
            "Hill": {'terrain': self.hill_terrain, 'background': 'images/hill_bg.jpg', 'color': (0, 153, 0)},
            "Desert": {'terrain': self.desert_terrain, 'background': 'images/desert_bg.jpeg', 'color': (236, 191, 13)},
            "Moon": {'terrain': self.moon_terrain, 'background': 'images/moon_bg.jpg', 'color': (205, 205, 205)}}
        map_names = [key for key in self.maps.keys()]
        self.type = random.choice(map_names) if type is 'Random' else type
        self.terrain = self.maps[self.type]['terrain'](screen_dims)
        self.screen_dims = screen_dims



    def draw(self):
        self.screen.fill((200,200,200))
        try:
            background = pygame.image.load(self.maps[self.type]['background'])
            background = pygame.transform.scale(background, self.screen_dims)
        except pygame.error as message:
            background = pygame.Surface(self.screen_dims)
            background.fill((135, 206, 250))
        background.set_alpha(200)
        self.screen.blit(background, (0,0))
        points = list(enumerate(self.terrain)) + [self.screen_dims, (0, self.screen_dims[1])]
        pygame.draw.polygon(self.screen, self.maps[self.type]['color'], points)


    '''
    We generate a function using four random numbers and draw
    polygon of that function over the pixels of the screen
    @param screen_dims is the tuple of (width, height) dimensions of the screen
    @return a list of heights of the terrain at various x positions on the screen
    '''
    def snow_terrain(self, screen_dims):
        a = random.randint(0.10 * screen_dims[1], 0.15 * screen_dims[1])
        b = random.randint(0.10 * screen_dims[1], 0.15 * screen_dims[1])
        c = random.randint(screen_dims[0]/50, screen_dims[0]/10)
        d = random.randint(screen_dims[0]/50, screen_dims[0]/10)
        return [0.5*screen_dims[1] - int(a * math.sin((1 + x) /c) + b * math.cos((1 + x) / d)) for x in range(screen_dims[0])]


    def hill_terrain(self, screen_dims):
        a = random.randint(0.05 * screen_dims[1], 0.08 * screen_dims[1])
        b = random.randint(0.05 * screen_dims[1], 0.08 * screen_dims[1])
        c = random.randint(screen_dims[0]/20, screen_dims[0]/10)
        d = random.randint(screen_dims[0]/20, screen_dims[0]/10)
        return [0.7*screen_dims[1] - int(a * math.sin((1 + x) /c) + b * math.cos((1 + x) / d)) for x in range(screen_dims[0])]

    def desert_terrain(self, screen_dims):
        a = random.randint(0.01 * screen_dims[1], 0.01 * screen_dims[1])
        b = random.randint(0.01 * screen_dims[1], 0.01 * screen_dims[1])
        c = random.randint(screen_dims[0]/5, screen_dims[0])
        d = random.randint(screen_dims[0]/5, screen_dims[0])
        return [0.9*screen_dims[1] - int(a * math.sin((1 + x) /c) + b * math.cos((1 + x) / d)) for x in range(screen_dims[0])]

    def moon_terrain(self, screen_dims):
        a = random.randint(0.01 * screen_dims[1], 0.01 * screen_dims[1])
        b = random.randint(0.01 * screen_dims[1], 0.01 * screen_dims[1])
        c = random.randint(screen_dims[0]/5, screen_dims[0])
        d = random.randint(screen_dims[0]/5, screen_dims[0])
        return [0.8*screen_dims[1] - int(a * math.sin((1 + x) /c) + b * math.cos((1 + x) / d)) for x in range(screen_dims[0])]

    def get_terrain(self):
        return self.terrain

    def set_terrain(self, terrain):
        self.terrain = terrain

    def apply_damage(self, center, radius):
        for x in range(center[0]-radius, center[0]+radius+1):
            if x<self.screen_dims[0] and x>0 and utils.dist(center,(x, self.terrain[x])) <= radius**2:
                new_height = int(center[1] + math.sqrt(radius**2 - (center[0] - x)**2))
                if new_height >= self.terrain[x]:
                    self.terrain[x] = new_height

    def dump(self, f):
        f.write(self.type+'\n')
        f.write(str(self.terrain)+'\n')



