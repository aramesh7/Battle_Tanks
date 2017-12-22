import pygame

'''
This is the class responsible for displaying all the game information on the screen for a given player

'''

class Gamestats:
    def __init__(self, screen, screen_dims):
        self.screen = screen
        self.name_font = pygame.font.SysFont('Times New Roman', 16, True)
        self.health_font = pygame.font.SysFont('Arial', 10, True)
        self.weapon_font = pygame.font.SysFont('Times New Roman', 15, True)
        self.money_font = pygame.font.SysFont('Monaco', 20, True)
        self.border_width = 2
        self.width = screen_dims[0]
        self.height = (screen_dims[1]/6)
        self.item_box = pygame.Surface((self.width, self.height))
        self.item_box.set_alpha(70)
        self.item_box.fill((220,220,220))
        self.border_color = (100,100,100)

    def draw(self, player):
        #Draw the border
        pygame.draw.rect(self.screen, self.border_color, [0,0,self.width,2]) #top
        pygame.draw.rect(self.screen, self.border_color, [0,0,2, self.height]) #left
        pygame.draw.rect(self.screen, self.border_color, [0,self.height - 2 ,self.width,2]) #bottom
        pygame.draw.rect(self.screen, self.border_color, [self.width - 2,0,2, self.height]) #right

        # Draw the item_box
        self.screen.blit(self.item_box, (2,2))

        #Draw the player name
        self.screen.blit(self.name_font.render(player.name, True, player.color),(5,5))

        #Draw the health/power_bar
        health_bar_height = int(0.8*self.height)
        loss = 100 - int(player.health)
        pixels_per_health = health_bar_height/100.0
        health_loss = int(loss*pixels_per_health)
        health_bar_x = self.width/5
        health_bar_y = int(0.1 * self.height)
        health_bar_width = 30

        #Health bar
        pygame.draw.rect(self.screen, (0,0,0), [health_bar_x ,health_bar_y ,health_bar_width, health_bar_height])
        pygame.draw.rect(self.screen, (255,0,0), [health_bar_x ,health_bar_y + health_loss ,health_bar_width, health_bar_height - health_loss])
        self.screen.blit(self.health_font.render(str(int(player.health)), True, (255,255,255)), (health_bar_x + (health_bar_width/5), health_bar_y + 2))


        #power bar
        power_height = (100 - player.power) * pixels_per_health
        pygame.draw.rect(self.screen, (0,0,0), [health_bar_x-4, health_bar_y + power_height, health_bar_width+8, 2])
        self.screen.blit(self.health_font.render(str(int(player.power)), True, (0,0,0)), (health_bar_x + health_bar_width + 5, health_bar_y + power_height))

        #Draw the fuel tank
        fuel_bar_x = self.width/30
        fuel_bar_y = self.height*0.7
        fuel_bar_width = 0.1 * self.width
        fuel_bar_height = 10

        pygame.draw.rect(self.screen, (0,0,0), [fuel_bar_x, fuel_bar_y, fuel_bar_width, 10])
        pygame.draw.rect(self.screen, (0,255,100), [fuel_bar_x, fuel_bar_y, int(fuel_bar_width*(player.fuel/player.max_fuel)), 10])
        self.screen.blit(self.health_font.render(str(int(player.fuel)), True, (0,0,0)), (fuel_bar_x + fuel_bar_width +2,fuel_bar_y+(fuel_bar_height/2)))

        # Display the current weapon
        weapon = player.current_weapon
        count = player.weapons[weapon]
        count = str(count) if count >=0 else '∞'
        weapon_x = health_bar_x + health_bar_width + 25
        weapon_y = 5
        self.screen.blit(self.weapon_font.render("Current Weapon: ", True, (0,0,0)), (weapon_x, weapon_y))
        self.screen.blit(self.weapon_font.render("Current Ammo: ", True, (0,0,0)), (weapon_x, weapon_y + 17))
        self.screen.blit(self.weapon_font.render(weapon, True, (255,0,0)), (weapon_x + 130, weapon_y))
        self.screen.blit(self.weapon_font.render(': '+count, True, (255,0,0)), (weapon_x + 120, weapon_y + 17))

        # Display total score

        self.screen.blit(self.money_font.render('$'+str(player.total_score), True, (255,150,0)), (weapon_x + 30, weapon_y + self.height/2))

    def set_last_save(self, time):
        pass






