import pygame as pyg
from pygame.locals import *
import sys
import json

with open('config.json') as config_json:
    # Carga los datos del archivo JSON
    configJSON = json.load(config_json)

with open('boxes.json') as boxes_json:
    # Carga los datos del archivo JSON
    boxesJSON = json.load(boxes_json)

# Otorgamos características a la ventana
backgroundColor = (0, 0, 0)
pyg.init()
Screen = pyg.display.set_mode((int(configJSON['screen']['width']), int(configJSON['screen']['height'])), RESIZABLE)  # Permite redimensionar la ventana
pyg.display.set_caption(title='Atomx')

#Obtiene la altura y anchura de la pantalla
screen_width, screen_height = Screen.get_size()

# Función para redimensionar la pantalla
def resizeScreen(width, height):
    global screen_height, screen_width
    Screen = pyg.display.set_mode((width, height), RESIZABLE)
    screen_width, screen_height = Screen.get_size()

posY = 300
posX = 400
radius = 3

# Bucle para iniciar y refrescar la ventana
clock = pyg.time.Clock()  # Crear un objeto Clock para controlar la velocidad del juego
velocity = (5, 5)  # Velocidad en dos dimensiones (horizontal, vertical)

while True:
    for event in pyg.event.get():
        if event.type == QUIT:  # Cerrar la ventana
            pyg.quit()
            sys.exit()
        elif event.type == VIDEORESIZE:  # Evento de redimensionar la ventana
            width, height = event.size
            resizeScreen(width, height)

    Screen.fill(backgroundColor)  # Limpiar la pantalla
    
    #Añadimos las cajas para contener las moleculas
    for box in boxesJSON:
        if box['display']:
            pyg.draw.rect(Screen, box['backgroundColorRGB'], (box['position'][0], box['position'][1], box['dimensions']['width'], box['dimensions']['height']), 1)

    # Actualiza la posición del círculo en ambas dimensiones
    posX += velocity[0]  # Componente horizontal de la velocidad
    posY += velocity[1]  # Componente vertical de la velocidad

    # Se invierte la dirección si la pelota llega a los bordes de la pantalla
    if posX + radius >= screen_width or posX - radius <= 0:
        velocity = (-velocity[0], velocity[1])
    if posY + radius >= screen_height or posY - radius <= 0:
        velocity = (velocity[0], -velocity[1])

    pyg.draw.circle(Screen, (255, 255, 255), (posX, posY), radius)  # Dibujar la pelota en la nueva posición
    pyg.display.update()  # Actualizar la pantalla

    clock.tick(60)  # Limitar la velocidad del juego a 60 fotogramas por segundo
