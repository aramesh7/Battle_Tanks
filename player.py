import pygame
import math
from Tanks import weapon,gamestats,utils
import json

'''
This is the player class. The part of the model that stores all the
player information such as
-	Position of tank
-	Current health of tank
-	Weapons/ammo of tank
-	Fuel in tank
-	Current cannon configuration
-	Current selected weapon
-	Added upgrades
-	Current score
-   Player Name
'''
TANK_SCALE = 3
TANK_HEIGHT = 7
TANK_WIDTH  = TANK_SCALE*TANK_HEIGHT
TURRET_WIDTH = int(math.sqrt(TANK_HEIGHT))
TURRET_LENGTH = 5*TANK_WIDTH/8
TURRET_SPEED = math.pi/20
class Player():
    def __init__(self, screen, game_map, name, color, init_x, init_y, screen_dims, fps):
        # necessary fields for drawing
        self.name = name
        self.screen = screen
        self.game_map = game_map
        self.fps = fps
        self.screen_width = screen_dims[0]
        self.screen_height = screen_dims[1]
        self.color = color
        self.rect = pygame.Rect((init_x-(TANK_WIDTH/2), init_y - (TANK_HEIGHT/2)), (TANK_WIDTH, TANK_HEIGHT))
        self.hatch_radius = int(5 * TANK_WIDTH / 16)
        self.turret_angle = 0
        self.turret_endpoint = (self.rect.centerx - TURRET_LENGTH*math.cos(self.turret_angle),self.rect.top - (self.hatch_radius/2) -TURRET_LENGTH*math.sin(self.turret_angle))
        self.speed = 3
        self.movement = [0, 0]
        self.death_radii = []

        # Game fields
        self.total_score = 0
        self.round_score = 0
        self.health = 100
        self.fuel = 300
        self.exploding = False
        self.destroyed = False

        #weapons
        self.current_weapon = "Missile"
        self.weapons = {"Missile":-1, "Heavy Missile":-1, "Volcano Bomb": 5,"Shower": 2, "Hot Shower": 2, "Nuke Shower": 1,  "Kiloton Bomb": 2, "Megaton Bomb": 1, "Gigaton Bomb": 1, "Precision Air Strike": -1}
        self.power = 0.5*self.health
        self.armor_scale_factor = 1
        self.max_fuel = 300
        self.upgrades = {"Upgrade Armor": 250, "Upgrade Speed": 0, "Add Fuel Capacity" : 300, "Health Recharge": 1}

        #statsbar
        self.stats =  gamestats.Gamestats(screen, screen_dims)

    '''
    The following functions all update the model as stored in the player
   
    '''

    '''
    The move function updates the player's tank configuration
    @param left is True iff the user wants to move left
    @param right is True iff the use wants to move right
    @param direction is 1 if turret is to move counter-clockwise -1 otherwise
    @param power_up is True iff the power needs to increase
    @param power_down is True iff the user is decreasing the power
    '''

    def move(self, left, right, direction, power_up, power_down):

        # Change position of tank
        if self.fuel > 0:
            if right:
                self.fuel = max(self.fuel - 1, 0)
                self.movement[0] = self.speed
            elif left:
                self.fuel = max(self.fuel - 1, 0)
                self.movement[0] = -self.speed
            else:
                self.movement = [0,0]
        else:
            self.movement = [0,0]
        self.rect.center = tuple(map(sum, zip(self.rect.center, self.movement)))
        if self.rect.left > self.screen_width:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = self.screen_width
        if self.rect.centerx > 0 and self.rect.centerx < self.screen_width:
            self.rect.centery = self.game_map.get_terrain()[self.rect.centerx]+(TANK_HEIGHT/2)

        # Adjust turret angle
        self.turret_angle += (direction * TURRET_SPEED)
        if self.turret_angle > math.pi:
            self.turret_angle = math.pi
        if self.turret_angle < 0:
            self.turret_angle = 0

        # adjust the power
        if power_up:
            self.power = min(self.health, self.power + 1)
        if power_down:
            self.power = max(self.power-1, 0)

    '''
    Place the player at a certain location on the map programmatically
    '''

    def place_player(self, x, y):
        self.rect.center = (x,y)

    '''
    Update the player's score based on whether the enemy was destroyed or
    if the player destroyed themselves etc.
    @param enemy player object caught in blast radius.
    '''

    def add_score(self, enemy):
        target_destroyed = enemy.exploding
        if enemy is not self:
            self.total_score += weapon.weapons[self.current_weapon]['damage']
            self.round_score += weapon.weapons[self.current_weapon]['damage']
            if target_destroyed:
                self.round_score += 300
                self.total_score += 300
        else:
            self.total_score -= weapon.weapons[self.current_weapon]['damage']
            self.round_score -= weapon.weapons[self.current_weapon]['damage']
            if target_destroyed:
                self.round_score -= 100
                self.total_score -= 100

    '''
    Allow the player to switch weapons back and forth
    '''
    def switch_weapon(self, direction):
        my_weapons = list(self.weapons.keys())
        self.current_weapon = my_weapons[(my_weapons.index(self.current_weapon) + direction)%len(my_weapons)]

    def upgrade(self, upgrade):
        if self.total_score>=weapon.upgrades[upgrade][0]:
            if upgrade == 'Add Fuel Capacity':
                self.upgrades[upgrade]+=weapon.upgrades[upgrade][1]
                self.max_fuel+=weapon.upgrades[upgrade][1]
            elif upgrade == 'Upgrade Armor':
                self.upgrades[upgrade]+=1
                self.armor_scale_factor = max(self.armor_scale_factor-0.1, 0.1)
            elif upgrade == 'Upgrade Speed':
                self.upgrades[upgrade]+=1
                self.speed+=2
            elif upgrade == 'Health Recharge':
                self.upgrades[upgrade]+=1
            else:
                return
            self.total_score-=weapon.upgrades[upgrade][0]

    '''
    This function updates the players weapons inventory
    '''
    def add_weapon(self, new_weapon):
        if self.total_score>=weapon.weapons[new_weapon]['cost']:
            if new_weapon not in self.weapons:
                self.weapons[new_weapon] = 0
            self.weapons[new_weapon]+=weapon.weapons[new_weapon]['gain']
            self.total_score-=weapon.weapons[new_weapon]['cost']


    '''
    This function is used for when new rounds start
    Resets any round scope stats of the player
    @param game_map receives the NEW game_map for the next round
    '''
    def reset_player_stats(self, new_game_map):
        self.round_score = 0
        self.fuel = self.max_fuel
        self.health = 100
        self.exploding = False
        self.destroyed = False
        self.power = 0.5*self.health
        self.movement = [0,0]
        self.game_map = new_game_map
        self.rect.centery = new_game_map.get_terrain()[self.rect.centerx]

    '''
    Draw function for the player class as well as helpers for when player explodes
    @param showstats is True if we need to show this players stats (i.e. it is this player's turn)
    '''

    def draw(self, show_stats):
        if show_stats:
            self.stats.draw(self)
       # if self.rect.centerx > 0 and self.rect.centerx < self.screen_width:
        #    self.rect.centery = self.game_map.get_terrain()[self.rect.centerx]+(TANK_HEIGHT/2)
        pygame.draw.rect(self.screen, self.color, self.rect)
        pygame.draw.circle(self.screen, self.color, (self.rect.centerx, self.rect.top) ,self.hatch_radius)
        turret_end_x = self.rect.centerx - TURRET_LENGTH*math.cos(self.turret_angle)
        turret_end_y = self.rect.top - (self.hatch_radius/2) -TURRET_LENGTH*math.sin(self.turret_angle)
        self.turret_endpoint = (turret_end_x, turret_end_y)
        pygame.draw.line(self.screen, self.color, (self.rect.centerx, self.rect.top - (self.hatch_radius/2)), self.turret_endpoint, TURRET_WIDTH)

    def draw_death(self):
        color, radius = self.death_radii.pop()
        pygame.draw.circle(self.screen, color, self.rect.center, radius)
        return True if self.death_radii else False


    '''
    Various helper functions for the attack dynamics of the game
    Most of these functions communicate with the weapons module
    '''

    def get_shot_trajectory(self):
        if not self.weapons[self.current_weapon]:
            return []
        self.weapons[self.current_weapon] = self.weapons[self.current_weapon] - 1
        return weapon.weapons[self.current_weapon]['get_path'](self.turret_endpoint, self.fps, self.power, self.turret_angle, self.game_map.get_terrain())

    def get_explosion_radii(self):
        blasts = weapon.explode(self.current_weapon, self.fps)
        return max([blast[1] for blast in blasts]),list(reversed(blasts))

    def get_shell_radius(self):
        return weapon.weapons[self.current_weapon]['shell_radius']

    def get_weapon_damage(self):
        return weapon.weapons[self.current_weapon]['damage']

    def apply_damage(self, damage):
        self.health = max(self.health - damage*self.armor_scale_factor, 0)
        if self.health<=0:
            self.exploding = True
            self.death_radii = weapon.explode('Death', self.fps)
        self.power = min(self.power, self.health)

    def health_recharge(self):
        if self.upgrades['Health Recharge']:
            self.upgrades['Health Recharge']-=1
            self.health+=50

    def in_blast_radius(self, epicenter, radius):
        l = self.rect.left
        r = self.rect.right

        # now calculate euclidean distances to key points and return whether they are within radius of epicenter
        if utils.dist(epicenter,self.rect.center) <= radius:
            return True
        elif utils.dist(epicenter, (l,self.rect.centery)) < radius or utils.dist(epicenter, (r, self.rect.centery)) < radius:
            return True
        else:
            return False

    '''
    Write out this player object to a file
    '''
    def dump(self, f):
        weapon_list = json.dumps(self.weapons)
        vars = [self.name,list(self.color),list(self.rect.center), self.speed, self.total_score, self.health, self.fuel, self.exploding, self.destroyed, self.current_weapon,weapon_list, self.power, self.armor_scale_factor,self.max_fuel]
        f.write('\n'.join(list(map(str, vars))))
        f.write('\n')

    '''
    Read this player object from a save file
    '''
    def load(self, fp):
        self.speed = int(fp.readline()[:-1])
        self.total_score = int(fp.readline()[:-1])
        self.health = int(fp.readline()[:-1])
        self.fuel = int(fp.readline()[:-1])
        self.exploding = fp.readline()[:-1]=='True'
        self.destroyed = fp.readline()[:-1]=='True'
        self.current_weapon = fp.readline()[:-1]
        self.weapons = json.loads((fp.readline()[0:-1]))
        self.power = float(fp.readline()[:-1])
        self.armor_scale_factor = int(fp.readline()[:-1])
        self.max_fuel = int(fp.readline()[:-1])