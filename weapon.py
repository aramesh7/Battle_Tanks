import pygame
import math

'''
This is a module with functions that define various types of weapons

CONSTANTS 
'''
velocity_scale_factor = 2.0
gravity_scale_factor = 3.0
time_resolution = 4.0
g = 9.8*gravity_scale_factor


'''
This is the dictionary (jump table) where we register a weapon by its name as the key, and the value is
a dictionary of functions related to that weapon
'''


'''
PATH 

The following functions are all jump table functions that calculate the trajectory
of various weapons given their initial position and initial velocity vector

@param start_pos is an (x,y) tuple representing the starting position of the missile
@param fps is the number of frames per second, helps determine the number of positions
@param initial_velocity is the power with which the missile was fired
@param angle the angle at which the missile is fired

#################################################################
'''
def trajectory(start_pos, fps, initial_velocity, angle, terrain):

    angle = math.pi - angle

    v_x = velocity_scale_factor*initial_velocity * math.cos(angle)
    v_y = -velocity_scale_factor*initial_velocity * math.sin(angle)
    #Calculate the time step
    time_unit = time_resolution/fps

    #Adjust the angle
    pos_x = int(start_pos[0])
    pos_y = int(start_pos[1])

    positions = [(pos_x, pos_y)]

    while int(pos_y) < terrain[int(pos_x)]:
        pos_x = pos_x + v_x * time_unit
        if int(pos_x)>=len(terrain):
            break
        pos_y = pos_y + v_y*time_unit + 0.5*g*time_unit**2
        v_y = v_y + g * time_unit
        positions.append((int(pos_x), int(pos_y)))

    return positions, math.sqrt((v_x**2 + v_y**2))

def missile_path(start_pos, fps, initial_velocity, angle, terrain):
    return [trajectory(start_pos, fps, initial_velocity, angle, terrain)[0]]

def volcano_path(start_pos, fps, initial_velocity, angle, terrain):
    initial_trajectory = trajectory(start_pos, fps, initial_velocity, angle, terrain)
    init_path = initial_trajectory[0]
    final_v = initial_trajectory[1]
    end_pos = init_path[-1]
    if end_pos[0]< len(terrain)-1 and end_pos[0]> 0:
        ground_angle = math.atan2(terrain[end_pos[0]+1] - terrain[end_pos[0]-1], 1)
    else:
        ground_angle = 0
    bounce_trajectories = []
    for i in range(3):
        bounce = trajectory((end_pos[0], terrain[end_pos[0]]-1), fps, final_v/5, ground_angle + i*(math.pi/4), terrain)[0]
        bounce_trajectories.append(init_path + bounce)
    return [init_path] + bounce_trajectories


def shower_path(start_pos, fps, initial_velocity, angle, terrain):
    trajectories = []
    for factor in [0.8, 0.9, 1, 1.1, 1.2]:
        trajectories.append(trajectory(start_pos, fps, factor*initial_velocity, angle, terrain)[0])
    return trajectories

def airstrike_path(start_pos, fps, initial_velocity, angle, terrain):
    global time_resolution
    selected = False
    while not selected:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                selected = True
                break
    save_time = time_resolution
    time_resolution = 6
    trajectories = [trajectory((x, 0), fps, -50, math.pi/2, terrain)[0]]
    time_resolution = save_time
    return trajectories






weapons = {
    "Missile": {'get_path':missile_path, 'shell_radius': 2, 'explosion_radius': 20, 'damage': 20,
                'end_factor': 0.2, 'cost': 0, 'gain': 0},
    "Heavy Missile": {'get_path':missile_path, 'shell_radius':3, 'explosion_radius': 30, 'damage': 30,
                      'end_factor': 0.2, 'cost': 0, 'gain': 0},
    "Volcano Bomb": {'get_path': volcano_path, 'shell_radius': 2, 'explosion_radius':20, 'damage': 40,
                     'end_factor': 0.2, 'cost': 150, 'gain': 5},
    "Kiloton Bomb": {'get_path':missile_path, 'shell_radius': 5, 'explosion_radius': 100, 'damage': 50,
                     'end_factor': 0.12, 'cost':300, 'gain': 2},
    "Megaton Bomb": {'get_path': missile_path, 'shell_radius': 7, 'explosion_radius': 200, 'damage': 100,
                     'end_factor': 0.1, 'cost': 600, 'gain': 1},
    "Gigaton Bomb": {'get_path': missile_path, 'shell_radius': 10, 'explosion_radius': 300, 'damage': 200,
                     'end_factor': 0.1, 'cost': 1000, 'gain': 1},
    "Shower": {'get_path': shower_path, 'shell_radius': 3, 'explosion_radius': 30, 'damage': 30,
                     'end_factor': 0.2, 'cost': 250, 'gain': 2},
    "Hot Shower": {'get_path': shower_path, 'shell_radius': 5, 'explosion_radius': 40, 'damage': 40,
                     'end_factor': 0.2, 'cost': 600, 'gain': 1},
    "Nuke Shower": {'get_path': shower_path, 'shell_radius': 7, 'explosion_radius': 80, 'damage': 60,
                     'end_factor': 0.2, 'cost': 1000, 'gain': 1},
    "Precision Air Strike":{'get_path': airstrike_path, 'shell_radius': 5, 'explosion_radius': 50, 'damage': 500,
                     'end_factor': 0.2, 'cost': 1000, 'gain': 1}
}

# Dictionary to map upgrade to cost,gain of upgrades
upgrades = {"Upgrade Armor": [250, 1],
            "Upgrade Speed": [150, 1],
            "Add Fuel Capacity" : [50,100],
            "Health Recharge": [350,1]}


def explode(type, fps):

    time_step = 1
    if type is 'Death':
        max_radius = 40
        end_radius_factor = 0.1
    else:
        max_radius = weapons[type]['explosion_radius']
        end_radius_factor = weapons[type]['end_factor']
    radii = []
    radius = 0
    time = 0

    #Controls the relative radius of the final size of the blast
    peak_color = 255.0

    while time < math.e - 1 or radius > end_radius_factor*max_radius:
        radius = max_radius*math.e*math.log1p(time)/(1+time)**1.5
        time+=time_step
        radii.append(int(radius))


    return list(map(lambda x: ((255, int(peak_color-x[0]*(peak_color/len(radii))),0),x[1])  , enumerate(radii)))

