import pygame as pyg
from pygame.locals import *
import sys
import json
import random

with open('settings/config.json') as config_json:
    configJSON = json.load(config_json)

with open('settings/boxes.json') as boxes_json:
    boxesJSON = json.load(boxes_json)

with open('settings/initialCondition.json') as condition_json:
    conditionJSON = json.load(condition_json)

icon = pyg.image.load('icon.png')
pyg.display.set_icon(icon)
backgroundColor = (0, 0, 0)
pyg.init()
Screen = pyg.display.set_mode((int(configJSON['screen']['width']), int(configJSON['screen']['height'])), RESIZABLE)
pyg.display.set_caption(title='Atomx')

screen_width, screen_height = Screen.get_size()

def resizeScreen(width, height):
    global screen_height, screen_width
    Screen = pyg.display.set_mode((width, height), RESIZABLE)
    screen_width, screen_height = Screen.get_size()

def getRandomPositions(num_molecules, box_dimensions):
    positions = set()
    while len(positions) < num_molecules:
        x = random.randint(0, box_dimensions['width'])
        y = random.randint(0, box_dimensions['height'])
        positions.add((x, y))
    return list(positions)

posXList = []
posYList = []
colors = []

def getMoleculesPositions():
    for box in boxesJSON:
        for mol in conditionJSON:
            if str(mol['gridType']) == 'random':
                if str(box['name']) == str(mol['box']):
                    box_dimensions = box['dimensions']
                    num_molecules = mol['number']
                    color = mol['colorRGB']
                    positions = getRandomPositions(num_molecules, box_dimensions)
                    for position in positions:
                        posXList.append(position[0] + box['position'][0])
                        posYList.append(position[1] + box['position'][1])
                        colors.append(color)
            elif str(mol['gridType']) == 'mesh':
                if str(box['name']) == str(mol['box']):
                    pass

getMoleculesPositions()

clock = pyg.time.Clock()

velXList = [random.uniform(-1, 1) for _ in posXList]
velYList = [random.uniform(-1, 1) for _ in posYList]

font = pyg.font.Font(None, 15)

while True:
    for event in pyg.event.get():
        if event.type == QUIT:
            pyg.quit()
            sys.exit()
        elif event.type == VIDEORESIZE:
            width, height = event.size
            resizeScreen(width, height)

    Screen.fill(backgroundColor)

    for box in boxesJSON:
        if box['display']:
            pyg.draw.rect(Screen, box['backgroundColorRGB'], (box['position'][0], box['position'][1], box['dimensions']['width'], box['dimensions']['height']), 1)
    
    for i in range(len(posXList)):
        posXList[i] += velXList[i]
        posYList[i] += velYList[i]
        
        if posXList[i] <= 0 or posXList[i] >= screen_width:
            velXList[i] *= -1
        if posYList[i] <= 0 or posYList[i] >= screen_height:
            velYList[i] *= -1
    
    for x, y, color in zip(posXList, posYList, colors):
        pyg.draw.rect(Screen, color, (x, y, 2, 2))
    
    # Renderizar y dibujar el texto de los FPS
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    Screen.blit(fps_text, (10, 10))
    
    pyg.display.update()

    clock.tick(60)
