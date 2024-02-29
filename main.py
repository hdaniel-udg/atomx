import pygame as pyg
from pygame.locals import *
import sys
import json
import random
import uuid
import math

# Un pixel en la pantalla equivale a un amstrong

class Box(pyg.sprite.Sprite):
    def __init__(self, name, position, dimensions, background_color, block):
        super().__init__()
        self.name = name
        self.block = block
        self.rect = pyg.Rect(position[0], position[1], dimensions['width'], dimensions['height'])
        self.image = pyg.Surface((self.rect.width, self.rect.height))
        pyg.draw.rect(self.image, background_color, self.image.get_rect(), width=1)  # Dibujamos el borde

    def createMolecules(self, condition_data):
        molecules = pyg.sprite.Group()
        for molecule_data in condition_data:
            if molecule_data['box'] == self.name:
                for _ in range(molecule_data['number']):
                    position = (random.randint(self.rect.left+(self.rect.left*0.03), self.rect.right-(self.rect.right*0.03)),
                                random.randint(self.rect.top+(self.rect.top*0.03), self.rect.bottom-(self.rect.bottom*0.03)))
                    velocity_x = random.uniform(-1, 1)
                    velocity_y = random.uniform(-1, 1)

                    while abs(velocity_x) < 0.5 or abs(velocity_y) < 0.5:
                        velocity_x = random.uniform(-1, 1)
                        velocity_y = random.uniform(-1, 1)

                    color = molecule_data['colorRGB']
                    mass = 0
                    for atom in atoms_data:
                        if atom['name'] == molecule_data['name']:
                            mass = atom['atomicMass']
                    for molecule in molecules_data:
                        if molecule['name'] == molecule_data['name']:
                            mass = molecule['properties']['molecularMass']
                    molecule = Molecule(molecule_data['box'], position, [velocity_x, velocity_y], color,
                                        int(molecule_data['radiusNm'] // 0.1), mass, uuid.uuid4())
                    molecules.add(molecule)
        return molecules


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
        if not paused:  # Solo actualiza si no está pausado
            # Colisión con los bordes de la pantalla
            if self.rect.left <= 0 or self.rect.right >= screen_width:
                self.velocity[0] *= -1
            if self.rect.top <= 0 or self.rect.bottom >= screen_height:
                self.velocity[1] *= -1

            # Colisión con las cajas
            for box in boxes:
                if box.block:
                    if self.rect.left-self.length == box.rect.left or self.rect.right+self.length == box.rect.right:
                        self.velocity[0] *= -1
                    if self.rect.top-self.length == box.rect.top or self.rect.bottom+self.length == box.rect.bottom:
                        self.velocity[1] *= -1

            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]

pyg.init()
icon = pyg.image.load('icon.png')
pyg.display.set_icon(icon)
Screen = pyg.display.set_mode((800, 600), RESIZABLE)
pyg.display.set_caption('Atomx')
screen_width, screen_height = Screen.get_size()


with open('settings/initialCondition.json') as condition_json:
    condition_data = json.load(condition_json)

with open('settings/molecules.json') as molecules_json:
    molecules_data = json.load(molecules_json)

with open('settings/atoms.json') as atoms_json:
    atoms_data = json.load(atoms_json)

with open('settings/boxes.json') as boxes_json:
    boxes_data = json.load(boxes_json)

boxes = pyg.sprite.Group()
molecules = pyg.sprite.Group()
for box_data in boxes_data:
    boxColor =  box_data['backgroundColorRGB']
    if not box_data['display']:
        boxColor = (0,0,0)
    box = Box(box_data['name'], box_data['position'], box_data['dimensions'], boxColor, box_data['block'])
    molecules.add(box.createMolecules(condition_data))
    boxes.add(box)

clock = pyg.time.Clock()
paused = False  # Variable para controlar el estado de pausa
while True:
    for event in pyg.event.get():
        if event.type == QUIT:
            pyg.quit()
            sys.exit()
        elif event.type == VIDEORESIZE:
            width, height = event.size
            Screen = pyg.display.set_mode((width, height), RESIZABLE)
            screen_width, screen_height = Screen.get_size()  
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                paused = not paused  # Cambiar el estado de pausa

    molecules.update()

    Screen.fill((0, 0, 0))
    boxes.draw(Screen)
    molecules.draw(Screen)

    fps_text = pyg.font.Font(None, 15).render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    #Pone la información respectiva de cada caja
    for box in boxes:
        details = pyg.font.Font(None, 17).render("Temperatura:",True,(255,255,255))
        Screen.blit(details, (box.rect.x, box.rect.y - 20))
    Screen.blit(fps_text, (10, 10))

    pyg.display.update()
    clock.tick(60)
