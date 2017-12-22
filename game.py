'''
This is the python  file/ class that is responsible for communicating
between the model, view, and controller. The main game loop will be present
in this file.

'''
import Tanks
import pygame
from Tanks.map import Map
from Tanks.player import Player
from Tanks import utils, weapon
import random
import os
import json
import sys

# Display
WIDTH = 700
HEIGHT = 500
SCREEN_DIMS = (WIDTH, HEIGHT)
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (50, 180, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 250)
ORANGE = (255, 100, 0)
YELLOW = (255, 255, 0)
GRAY = (100,100,100)
GOLD = (255,150,0)


'''
This function reads from the model and updates the view.
Draws any changes in the screen.
'''
def update_view(screen, clock, players, turn, game_map, missile_trajectories, round_num=0):
    # Draw the view
    draw_elements(screen, game_map, players, turn, round_num)
    explosions = []
    while missile_trajectories or explosions:
        clock.tick(FPS)
        # Capture missile positions and explosions in this list
        positions = []
        # synthesize the current positions of all missile on the screen
        for trajectory in missile_trajectories:
            positions.append(trajectory.pop())
            if not trajectory:
                max_radius, radii = players[turn].get_explosion_radii()
                calculate_and_apply_damage(players, turn, game_map, positions[-1], max_radius)
                explosions.append([positions[-1],radii])

        # Draw each missile
        for missile_position in positions:
            pygame.draw.circle(screen, GRAY , missile_position, players[turn].get_shell_radius())
            if missile_position[1]%2==0:
                pygame.draw.circle(screen, RED , missile_position, max(players[turn].get_shell_radius() - 3,0))

        if explosions:
            for e in explosions:
                pos = e[0]
                color, radius = e[1].pop()
                pygame.draw.circle(screen, color, pos , radius)
            explosions = [e for e in explosions if e[1]]

        pygame.display.flip()
        draw_elements(screen, game_map, players, turn, round_num)
        missile_trajectories = [t for t in missile_trajectories if t]

    pygame.display.flip()


def draw_elements(screen, game_map, players, turn, round_num):
    game_map.draw()
    for index, player in enumerate(players):
        if not player.destroyed:
            if player.exploding:
                if not player.draw_death():
                    player.destroyed = True
            else:
                if turn == index:
                    player.draw(True)
                else:
                    player.draw(False)
    ranked = sorted(players, key=lambda p: p.round_score, reverse=True)
    round_font = pygame.font.SysFont('Calibri', 25, True, True)
    round_font.set_underline(True)
    screen.blit(round_font.render('Round: '+str(round_num), True, BLACK),(3 * WIDTH / 4, (HEIGHT / 6)))
    for index, player in enumerate(ranked):
        screen.blit(pygame.font.SysFont('Calibri', 20, True, True).render(player.name+' : '+str(player.round_score), True, player.color),
                    (3*WIDTH/4, (HEIGHT/6 + 10) + (index+1)*20))



'''
This function iterates through the players after a missile is fired and updates
the model (health, live status, score) accordingly
'''

def calculate_and_apply_damage(players, turn, game_map, position, max_radius):
    damage = players[turn].get_weapon_damage()
    game_map.apply_damage(position ,max_radius)
    for player in players:
        if player.in_blast_radius(position, max_radius):
            player.apply_damage(damage)
            players[turn].add_score(player)


'''
This function handles the view and model for the weapon store interface
allowing players to buy weapons, and decrementing their score accordingly
'''

def open_store(screen, clock, players):
    try:
        tankImg = pygame.image.load('Tanks/images/tank_weapon.jpg')
        tankImg = pygame.transform.scale(tankImg, (WIDTH, HEIGHT))
    except pygame.error as message:
        tankImg = pygame.Surface(SCREEN_DIMS)
        tankImg.fill(GREEN)
    item_box = pygame.Surface((4 * WIDTH / 5, 4 * HEIGHT / 5))
    item_box.set_alpha(150)
    item_box.fill((100, 100, 100))

    option_x = (WIDTH/10) + 15
    option_y = (HEIGHT/10) + 60
    option_w = 2*WIDTH/5 - 60
    option_h = 30



    # Load game or new game
    for player in players:
        #  A button will be a rectangle, a tiny square and a weapon name
        buttons = []
        store_items = list(weapon.weapons.keys()) + list(weapon.upgrades.keys())
        for w in store_items:
            name_rect = pygame.Surface((option_w, option_h))
            name_rect.set_alpha(150)
            name_rect.fill(WHITE)
            num_rect = pygame.Surface((option_h, option_h))
            num_rect.set_alpha(150)
            num_rect.fill(WHITE)
            buttons.append((name_rect,num_rect, w))
        done = False
        while not done:
            clock.tick(FPS)
            screen.fill(GREEN)
            screen.blit(tankImg, (0,0))
            screen.blit(item_box, (WIDTH / 10, HEIGHT / 10))
            screen.blit(pygame.font.SysFont('Arial', 20, True).render(player.name + ' : You have $' + str(player.total_score), True, GOLD),
                        (WIDTH / 4 + 30 , HEIGHT/10 + 20))
            for i,button in enumerate(buttons):
                # How much does the player have alreay
                if button[2] in player.weapons:
                    quantity = str(player.weapons[button[2]]) if player.weapons[button[2]] >= 0 else '∞'
                    cost = str(weapon.weapons[button[2]]['cost'])
                    gain = str(weapon.weapons[button[2]]['gain'])
                elif button[2] in player.upgrades:
                    quantity = str(player.upgrades[button[2]])
                    cost = str(weapon.upgrades[button[2]][0])
                    gain = str(weapon.upgrades[button[2]][1])
                else:
                    quantity = str(0)
                    cost = str(weapon.weapons[button[2]]['cost'])
                    gain = str(weapon.weapons[button[2]]['gain'])

                screen.blit(button[0],(option_x + int((i/9))*(option_w + (option_h + 5) + 20), option_y + (i%9)*(option_h + 5)))

                screen.blit(pygame.font.SysFont('Arial', 13, True).render(button[2] + ' : : ' + gain + ' for $' + cost, True, BLACK),
                            (option_x + int((i / 9)) * (option_w + (option_h + 5) + 20) + 10, option_y + (i % 9) * (option_h + 5) + 10))

                screen.blit(button[1],(option_x + int((i/9))*(option_w + (option_h + 5) + 20) +  (option_w +5), option_y+(i%9)*(option_h + 5)))

                screen.blit(pygame.font.SysFont('Arial', 13, True).render(quantity, True, BLACK),
                            (option_x + int((i / 9)) * (option_w + (option_h + 5) + 20) + (option_w +5) + 5,
                             option_y + (i % 9) * (option_h + 5) + 10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x,y = pygame.mouse.get_pos()
                    choice = get_selection(buttons, x, y,option_x, option_y, option_w, option_h)
                    if choice in weapon.weapons:
                        player.add_weapon(choice)
                    elif choice in weapon.upgrades:
                        player.upgrade(choice)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True
                        break
            pygame.display.flip()

'''
A helper function the store uses to get the button name that the user has clicked 
'''
def get_selection(buttons, x, y, option_x, option_y, option_w, option_h):
    # Remember that buttons is (Rect1, Rect1, name), we are trying to return the name of any collisions with Rect 1
    selected_buttons = [button for (i,button) in list(enumerate(buttons)) if pygame.Rect((option_x + int((i/9))*(option_w + (option_h + 5) + 20), option_y + (i%9)*(option_h + 5)),button[0].get_size()).collidepoint(x,y)]
    # This should be either an empty list or a list of 1
    return selected_buttons[0][2] if selected_buttons else None


'''
This function just draws the opening tanks sequence
'''

def opening_sequence(screen, clock):
    try:
        tankImg = pygame.image.load('Tanks/images/tank_main.jpg')
        tankImg = pygame.transform.rotozoom(tankImg, 0, WIDTH / 700)
    except pygame.error as message:
        tankImg = pygame.Surface(SCREEN_DIMS)
        tankImg.fill(GREEN)
    i = 0
    while True:
        i+=20
        clock.tick(FPS)
        screen.fill(GREEN)
        screen.blit(tankImg, (int(WIDTH/70),int(HEIGHT/30)))
        screen.blit(pygame.font.SysFont('Calibri', int(WIDTH/10), True, True).render('BATTLE TANKS', True, RED if (i/40)%2==0 else YELLOW), (int(WIDTH/15), min(i, int(7*HEIGHT/10))))
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit(0)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return
        pygame.display.flip()


'''
Show a list of load files, and load the one that gets clicked on.
'''
def load_game(screen, clock, item_box, tankImg):

    save_file_names = os.listdir('Tanks/saved_games')
    if not save_file_names:
        return
    r_h = min(30,int((2*HEIGHT/3)/len(save_file_names)))
    r_w = (2*WIDTH/3) - (WIDTH/10)
    r_x = (WIDTH/6) + (WIDTH/20)
    r_y_start = HEIGHT/5 + 30
    rectangles = []
    for i in range(len(save_file_names)):
        rectangles.append(pygame.Rect([r_x, r_y_start + i * (r_h+5), r_w, r_h]))
    done = False

    # Let the user choose the load file
    while not done:
        clock.tick(FPS)
        screen.fill(GREEN)
        screen.blit(tankImg, (WIDTH / 6, HEIGHT / 10))
        screen.blit(item_box, (WIDTH / 6, HEIGHT / 6))
        screen.blit(pygame.font.SysFont('Arial', 25, True).render('Choose Save File', True, BLACK), (WIDTH/4 + 60, HEIGHT/6 + 10))
        for i in range(len(save_file_names)):
            pygame.draw.rect(screen, GRAY, rectangles[i])
            screen.blit(pygame.font.SysFont('Arial',20, True).render(save_file_names[i], True, WHITE),
                        (r_x + 10, r_y_start + i*(r_h+5)+3))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return [], None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    choices = [r.collidepoint(x,y) for r in rectangles]
                    if True in choices:
                        load_file = save_file_names[choices.index(True)]
                        done = True
                        break
        pygame.display.flip()

    players = []
    # Read the load file and initialize players and map
    with open('Tanks/saved_games/'+load_file) as f:

        # First read the map
        type = f.readline()[:-1]
        game_map = Map(screen, type, SCREEN_DIMS)
        terrain = list(map(float, (f.readline()[1:-2]).split(', ')))
        game_map.set_terrain(terrain)

        # Read the number of players
        num_players = int(f.readline()[:-1])
        for i in range(num_players):
            #Read the name, color and center
            name = f.readline()[:-1]
            color = tuple(json.loads(f.readline()[:-1]))
            init_x, init_y = tuple(json.loads(f.readline()[:-1]))

            #Create the player
            player = Player(screen, game_map, name, color,init_x, init_y, SCREEN_DIMS, FPS)

            #Load the player stats
            player.load(f)
            players.append(player)

    return players, game_map


'''
Allows the player to save the current game state to a file
'''

def save_game(screen, clock, game_map, players):

    name = ''
    done = False
    while not done:
        clock.tick(FPS)
        pygame.draw.rect(screen, BLACK, [WIDTH/3 - 2, (HEIGHT / 6) + 78, WIDTH / 3 + 4, 44])
        pygame.draw.rect(screen, GRAY, [WIDTH/3, (HEIGHT / 6) + 80, WIDTH / 3, 40])
        screen.blit(pygame.font.SysFont('Calibri', 20, True).render(name, True, WHITE),
                    (WIDTH/3 + 10, HEIGHT / 6 + 85))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return [], None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    done = True
                    break
                elif event.key==pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
        pygame.display.flip()

    with open('Tanks/saved_games/'+name+'.txt', 'w+') as f:
        game_map.dump(f)
        f.write(str(len(players))+'\n')
        for player in players:
            player.dump(f)


'''
This long function runs through the entire main menu sequence from 
choosing the number of players to choosing the names and colors of each player
'''

def main_menu_sequence(screen, clock):

    try:
        tankImg = pygame.image.load('Tanks/images/tank_menu.jpg')
        tankImg = pygame.transform.rotozoom(tankImg, 0, WIDTH / 600)
    except pygame.error as message:
        tankImg = pygame.Surface(SCREEN_DIMS)
        tankImg.fill(GREEN)
    item_box = pygame.Surface((2*WIDTH/3, 2*HEIGHT/3))
    item_box.set_alpha(200)
    item_box.fill((220, 220, 220))

    done = False

    # Load game or new game
    while not done:
        clock.tick(FPS)
        screen.fill(GREEN)
        screen.blit(tankImg, (WIDTH / 6, HEIGHT / 10))
        screen.blit(item_box, (WIDTH / 6, HEIGHT / 6))
        new_button= pygame.Rect([(WIDTH / 4) + 50, (HEIGHT / 6) + 80, WIDTH / 3, 60])
        load_button = pygame.Rect([(WIDTH / 4) + 50, (HEIGHT / 6) + 200, WIDTH / 3, 60])
        pygame.draw.rect(screen, GRAY, new_button)
        screen.blit(pygame.font.SysFont('Arial', 25, True).render('New Game', True, WHITE), ((WIDTH/4) + 100, HEIGHT/6 + 97))
        pygame.draw.rect(screen, GRAY, load_button)
        screen.blit(pygame.font.SysFont('Arial', 25, True).render('Load Game', True, WHITE), ((WIDTH/4) + 100, HEIGHT/6 + 217))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return [], None
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                if new_button.collidepoint(x,y):
                    done = True
                    break
                elif load_button.collidepoint(x,y):
                    return load_game(screen, clock, item_box, tankImg)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    done = True
                    break
        pygame.display.flip()


    #Set default number of players to 2
    num_players = 2
    done = False

    #Choose the number of players
    while not done:
        clock.tick(FPS)
        screen.fill(GREEN)
        screen.blit(tankImg, (WIDTH/6,HEIGHT/10))
        screen.blit(item_box,(WIDTH/6, HEIGHT/6))
        screen.blit(pygame.font.SysFont('Arial', 25, True).render('Enter the Number of Players', True, BLACK), (WIDTH/4, HEIGHT/6 + 30))
        screen.blit(pygame.font.SysFont('Arial', 100, True).render(str(num_players), True, BLACK), (WIDTH/2 - 30, HEIGHT/3 + 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return [], None
            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key).isdigit():
                    num_players = int(pygame.key.name(event.key))
                elif event.key == pygame.K_RETURN:
                    done = True
                    break
        pygame.display.flip()

    done = False
    #Choose the map

    radio_start_x =  int(WIDTH/4) +20
    radio_start_y = int(HEIGHT/6) + 100
    text_start_x = int(WIDTH/4) + 45
    text_start_y = int(HEIGHT/6) + 85
    vertical_spacing = 40
    options = ["Snow", "Hill", "Desert", "Moon", "Random"]
    radio_centers = [(radio_start_x , radio_start_y + vertical_spacing*i) for i in range(len(options))]

    #Set default choice to Random
    chosen_pos = len(options)-1

    while not done:
        clock.tick(FPS)
        screen.fill(GREEN)
        screen.blit(tankImg, (WIDTH/6,HEIGHT/10))
        screen.blit(item_box,(WIDTH/6, HEIGHT/6))
        screen.blit(pygame.font.SysFont('Calibri', 25, True).render('Choose Terrain Type', True, BLACK),(WIDTH/4, HEIGHT/6 + 30))
        for i, option in enumerate(options):
            pygame.draw.circle(screen, WHITE, (radio_start_x , radio_start_y + vertical_spacing*i), 10)
            screen.blit(pygame.font.SysFont('Calibri', 20, True).render(option, True, BLACK),(text_start_x, text_start_y + vertical_spacing*i))
        pygame.draw.circle(screen, BLACK, (radio_start_x , radio_start_y + vertical_spacing*chosen_pos), 7)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return [], None
            if event.type == pygame.MOUSEBUTTONDOWN:
                 chosen_pos = get_choice(radio_centers, chosen_pos, pygame.mouse.get_pos())
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    done = True
                    break
        pygame.display.flip()


    # Set the map name here
    chosen_map = options[chosen_pos]

    #Name players and choose player color

    colors = [RED, GREEN, YELLOW, BLUE, BLACK]
    names_and_colors = []
    color_start_x = int(WIDTH / 4) + 20
    color_start_y = int(2*HEIGHT/6) + 150
    horizontal_spacing = 40
    color_centers = [(color_start_x + horizontal_spacing*i, color_start_y) for i in range(len(colors))]


    for i in range(1,num_players+1):
        done = False
        # Set default color to 0 and name to empty
        name = 'Player '+str(i)
        chosen_color = 0
        while not done:
            clock.tick(FPS)
            screen.fill(GREEN)
            screen.blit(tankImg, (WIDTH / 6, HEIGHT / 10))
            screen.blit(item_box, (WIDTH / 6, HEIGHT / 6))
            screen.blit(pygame.font.SysFont('Calibri', 25, True).render('Enter Player '+str(i)+"'s Name: ", True, BLACK),
                        (WIDTH / 4, HEIGHT / 6 + 30))
            screen.blit(pygame.font.SysFont('Calibri', 25, True).render('Choose Player '+str(i)+"'s Color: ", True, BLACK),
                        (WIDTH / 4, 2*HEIGHT / 6 + 60))

            pygame.draw.rect(screen, WHITE, [(WIDTH / 4), (HEIGHT / 6)  + 80, WIDTH/3 , 40])

            screen.blit(pygame.font.SysFont('Calibri', 20, True).render(name, True, colors[chosen_color]),
                        (WIDTH / 4 + 10, HEIGHT / 6 + 85))

            for j, color in enumerate(colors):
                pygame.draw.circle(screen, color, color_centers[j], 10)

            #Fill in chosen option
            pygame.draw.circle(screen, GRAY, color_centers[chosen_color], 7)

            #Register the events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return [], None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    chosen_color = get_choice(color_centers, chosen_color, pygame.mouse.get_pos())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True
                        names_and_colors.append((name, colors[chosen_color]))
                        break
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name+=event.unicode

            pygame.display.flip()

    game_map = Map(screen, chosen_map, SCREEN_DIMS)
    terrain = game_map.get_terrain()
    players = [Player(screen, game_map, names_and_colors[i][0], names_and_colors[i][1],
                      (i+1)*WIDTH/(num_players+1) , terrain[int((i+1)*WIDTH/(num_players+1))], SCREEN_DIMS, FPS)
               for i in range(num_players)]

    return players, game_map


'''
A helper function to get the selected position for radio buttons
given a list of centers and clicked position
@return index of choice
'''
def get_choice(centers, curr_pos, new_pos):
    in_radius = [utils.dist(center, new_pos) <= 10 for center in centers]
    if any(in_radius):
        return in_radius.index(True)
    return curr_pos


'''
This function is used to check whether a given round has ended
(When 1 or fewer players are left standing)
'''

def game_ended(players):
    return sum([0 if (p.destroyed or p.exploding) else 1 for p in players ])<=1



'''
This loop handles everything related to input events like mouse clicks
and key presses and updates the model
'''

def game_sequence(screen, clock, game_map, players, round_number):
    num_players = len(players)
    turn = 0
    rotation = 0
    right = False
    left = False
    power_up = False
    power_down = False
    firing = False
    while not game_ended(players):
        clock.tick(FPS)
        missile_trajectories = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    right = True
                    left = False
                elif event.key == pygame.K_LEFT:
                    left = True
                    right = False
                elif event.key == pygame.K_UP:
                    rotation = 1
                elif event.key == pygame.K_DOWN:
                    rotation = -1
                elif event.key == pygame.K_SPACE:
                    missile_trajectories = [list(reversed(t)) for t in players[turn].get_shot_trajectory()]
                    if not missile_trajectories:
                        continue
                    firing = True
                    right = False
                    left = False
                elif event.key == pygame.K_x:
                    power_up = True
                    power_down = False
                elif event.key == pygame.K_z:
                    power_up = False
                    power_down = True
                elif event.key == pygame.K_s:
                    players[turn].switch_weapon(1)
                elif event.key == pygame.K_a:
                    players[turn].switch_weapon(-1)
                elif event.key == pygame.K_ESCAPE:
                    save_game(screen, clock,game_map, players)
                elif event.key == pygame.K_r:
                    players[turn].health_recharge()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    right = False
                if event.key == pygame.K_LEFT:
                    left = False
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    rotation = 0
                if event.key == pygame.K_x:
                    power_up = False
                if event.key == pygame.K_z:
                    power_down = False
        update_view(screen, clock, players, turn, game_map, missile_trajectories, round_number)
        players[turn].move(left, right, rotation, power_up, power_down)
        if firing:
            firing = False
            while True:
                turn = (turn + 1) % num_players
                if not players[turn].exploding:
                    break
                if game_ended(players):
                    return True
    return True



'''
The main function is responsible for orchestrating the 
transitions between various sequences in the game
'''

def main():
    # Initialize pygame and create window
    round_num = 1
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Battle Tanks")
    clock = pygame.time.Clock()

    #Run the opening sequence
    opening_sequence(screen, clock)

    #Generate the players and the game map based on user input
    players, game_map = main_menu_sequence(screen, clock)

    if not players or not game_map:
        return

    #Start the game_sequence
    while True:
        if not game_sequence(screen, clock, game_map, players, round_num):
            return
        else:

            open_store(screen, clock, players)
        game_map = Map(screen, "Random", SCREEN_DIMS)
        for player in players:
            player.reset_player_stats(game_map)
        random.shuffle(players)

if __name__ == '__main__':
    main()
