import pygame as pyg
from pygame.locals import *
import sys
import json
import random
import uuid
import math

# Un pixel en la pantalla equivale a un amstrong

class Box(pyg.sprite.Sprite):
    def __init__(self, name, position, dimensions, background_color):
        super().__init__()
        self.name = name
        self.rect = pyg.Rect(position[0], position[1], dimensions['width'], dimensions['height'])
        self.image = pyg.Surface((self.rect.width, self.rect.height))
        pyg.draw.rect(self.image, background_color, self.image.get_rect(), width=1)  # Dibujamos el borde

class Molecule(pyg.sprite.Sprite):
    def __init__(self, boxName, position, velocity, color, length, mass, uuid):
        super().__init__()
        self.boxName = boxName
        self.uuid = uuid
        self.mass = mass
        self.length = length
        self.rect = pyg.Rect(position[0], position[1], length, length)
        self.image = pyg.Surface((length, length), pyg.SRCALPHA)
        pyg.draw.rect(self.image, color, self.image.get_rect(), width=0)  # Dibujamos un cuadrado sólido
        self.velocity = velocity

    def update(self):
        

        # Colisión con los bordes de la pantalla
        if self.rect.left <= 0 or self.rect.right >= screen_width:
            self.velocity[0] *= -1
        if self.rect.top <= 0 or self.rect.bottom >= screen_height:
            self.velocity[1] *= -1

        # Colisión con las cajas
        for box in boxes:
            if box.name == self.boxName:
                if self.rect.left-self.length <= box.rect.left or self.rect.right+self.length >= box.rect.right:
                    self.velocity[0] *= -1
                if self.rect.top-self.length <= box.rect.top or self.rect.bottom+self.length >= box.rect.bottom:
                    self.velocity[1] *= -1

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

# Define una cuadrícula espacial con celdas de tamaño 100x100
class SpatialGrid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = [[[] for _ in range(width // cell_size)] for _ in range(height // cell_size)]

    def insert(self, sprite):
        row = sprite.rect.y // self.cell_size
        col = sprite.rect.x // self.cell_size
        self.grid[row][col].append(sprite)

    def get_sprites_in_cell(self, row, col):
        return self.grid[row][col]

    def clear(self):
        self.grid = [[[] for _ in range(self.width // self.cell_size)] for _ in range(self.height // self.cell_size)]


def detect_collisions_in_cell(cell_sprites):
    for i in range(len(cell_sprites)):
        for j in range(i+1, len(cell_sprites)):
            sprite1 = cell_sprites[i]
            sprite2 = cell_sprites[j]
            #if pyg.sprite.collide_rect(sprite1, sprite2):
                #print("Collision detected between:", sprite1.uuid, sprite2.uuid)
                #pyg.time.wait(500)
                # Agregar aquí la lógica para manejar la colisión

pyg.init()
icon = pyg.image.load('icon.png')
pyg.display.set_icon(icon)
Screen = pyg.display.set_mode((800, 600), RESIZABLE)
pyg.display.set_caption('Atomx')
screen_width, screen_height = Screen.get_size()

with open('settings/boxes.json') as boxes_json:
    boxes_data = json.load(boxes_json)

boxes = pyg.sprite.Group()
for box_data in boxes_data:
    box = Box(box_data['name'], box_data['position'], box_data['dimensions'], box_data['backgroundColorRGB'])
    boxes.add(box)

with open('settings/initialCondition.json') as condition_json:
    condition_data = json.load(condition_json)

with open('settings/molecules.json') as molecules_json:
    molecules_data = json.load(molecules_json)

with open('settings/atoms.json') as atoms_json:
    atoms_data = json.load(atoms_json)


grid = SpatialGrid(screen_width, screen_height, 100)  # Define una cuadrícula espacial con celdas de tamaño 100x100

molecules = pyg.sprite.Group()
for box_data in boxes_data:
    for molecule_data in condition_data:
        if molecule_data['box'] == box_data['name']:
            for _ in range(molecule_data['number']):
                position = (random.randint(box_data['position'][0] + box_data['dimensions']['width'] // 10, box_data['position'][0] + box_data['dimensions']['width'] - box_data['dimensions']['width'] // 10),
                            random.randint(box_data['position'][1] + box_data['dimensions']['height'] // 10, box_data['position'][1] + box_data['dimensions']['height'] - box_data['dimensions']['height'] // 10))
                velocity_x = random.uniform(-1, 1)
                velocity_y = random.uniform(-1, 1)
                
                while (velocity_x < 0.5 and velocity_x > -0.5) or (velocity_y< 0.5 and velocity_y > -0.5):
                    if velocity_x < 0.5 and velocity_x > -0.5:
                        velocity_x = random.uniform(-1, 1)
                    elif velocity_y< 0.5 and velocity_y > -0.5: 
                        velocity_y= random.uniform(-1, 1)
                
                color = molecule_data['colorRGB']
                mass = 0
                for atom in atoms_data:
                    if atom['name'] == molecule_data['name']:
                        mass = atom['atomicMass']
                for molecule in molecules_data:
                    if molecule['name'] == molecule_data['name']:
                        mass = molecule['properties']['molecularMass']
                molecule = Molecule(molecule_data['box'], position, [velocity_x, velocity_y], color, int(molecule_data['radiusNm']//0.1) , mass, uuid.uuid4()) #int(molecule_data['radiusNm']//0.1) Calcula la relación entre el radio atomico de van der waals en las codiciones iniciales y la correspondencia de 1px -> 1 Amstrong
                molecules.add(molecule)
                grid.insert(molecule)

clock = pyg.time.Clock()
font = pyg.font.Font(None, 15)

while True:
    for event in pyg.event.get():
        if event.type == QUIT:
            pyg.quit()
            sys.exit()
        elif event.type == VIDEORESIZE:
            width, height = event.size
            Screen = pyg.display.set_mode((width, height), RESIZABLE)
            screen_width, screen_height = Screen.get_size()  

    molecules.update()

    # Limpia la cuadrícula antes de insertar las moléculas en la nueva iteración
    grid.clear()

    # Inserta las moléculas en la cuadrícula
    for molecule in molecules:
        grid.insert(molecule)

    # Itera sobre cada celda de la cuadrícula y verifica colisiones entre moléculas en la misma celda o en celdas adyacentes
    for row in range(len(grid.grid)):
        for col in range(len(grid.grid[row])):
            cell_sprites = grid.get_sprites_in_cell(row, col)
            if cell_sprites:
                detect_collisions_in_cell(cell_sprites)

    Screen.fill((0, 0, 0))
    boxes.draw(Screen)
    molecules.draw(Screen)

    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    for box in boxes:
        details = pyg.font.Font(None, 17).render("Temperatura:",True,(255,255,255))
        Screen.blit(details, (box.rect.x, box.rect.y - 20))
    Screen.blit(fps_text, (10, 10))

    pyg.display.update()
    clock.tick(60)
