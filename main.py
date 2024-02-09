import pygame as pyg
from pygame.locals import *
import sys
import json
import random
import uuid

class Box(pyg.sprite.Sprite):
    def __init__(self, name, position, dimensions,background_color):
        super().__init__()
        self.name = name
        self.rect = pyg.Rect(position[0], position[1], dimensions['width'], dimensions['height'])
        self.image = pyg.Surface((self.rect.width, self.rect.height))
        pyg.draw.rect(self.image, background_color, self.image.get_rect(), width=1)  # Dibujamos el borde
        
class Molecule(pyg.sprite.Sprite):
    def __init__(self, boxName, position, velocity, color, diametro, mass, uuid):
        super().__init__()
        self.boxName = boxName
        self.uuid = uuid
        self.mass = mass
        self.diametro = diametro
        self.rect = pyg.Rect(position[0], position[1], diametro, diametro)
        self.image = pyg.Surface((diametro, diametro))
        self.image.fill(color)
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
                if not box.rect.contains(self.rect):
                    # Si la molécula está fuera de la caja, rebotar con la caja
                    if self.rect.left < box.rect.left or self.rect.right > box.rect.right:
                        self.velocity[0] *= -1
                    if self.rect.top < box.rect.top or self.rect.bottom > box.rect.bottom:
                        self.velocity[1] *= -1

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        
        # Colisión con otras moléculas
        #for molecule in molecules:
        #    collisions = pyg.sprite.spritecollide(molecule, molecules, False)
            #Moleculas con las que choca
        #    for collided_molecule in collisions:
        #        if collided_molecule != molecule:
        #            self.setVelocity(molecule, collided_molecule)
                    #print(molecule.uuid, collided_molecule.uuid)

    
    def calculateColision(self, molecule, collided_molecule):
        pass
        #Ambos se diregen 
        #print('Calcular nueva', self.mass)
        #pyg.time.wait(2000)
        #Calcular la colision o el comportamiendo de las moleculas con el modelo de Lennar - Jones o Mecanica clasica de colisiones

pyg.init()
# Carga el icono
icon = pyg.image.load('icon.png')
# Establece el icono de la ventana
pyg.display.set_icon(icon)
Screen = pyg.display.set_mode((800, 600), RESIZABLE)
pyg.display.set_caption('Atomx')
screen_width, screen_height = Screen.get_size()

# Cargar datos de las cajas desde el archivo JSON
with open('settings/boxes.json') as boxes_json:
    boxes_data = json.load(boxes_json)

# Crea instancias de las cajas
boxes = pyg.sprite.Group()
for box_data in boxes_data:
    box = Box(box_data['name'], box_data['position'], box_data['dimensions'], box_data['backgroundColorRGB'])
    boxes.add(box)

# Cargar datos de las condiciones iniciales desde el archivo JSON
with open('settings/initialCondition.json') as condition_json:
    condition_data = json.load(condition_json)
# Cargar datos de las moléculas desde el archivo JSON
with open('settings/molecules.json') as molecules_json:
    molecules_data = json.load(molecules_json)
# Cargar datos de los atomos desde el archivo JSON
with open('settings/atoms.json') as atoms_json:
    atoms_data = json.load(atoms_json)

# Crea instancias de las moléculas
molecules = pyg.sprite.Group()
for box_data in boxes_data:
    for molecule_data in condition_data:
        if molecule_data['box'] == box_data['name']:
            for _ in range(molecule_data['number']):
                position = (random.randint(box_data['position'][0] + box_data['dimensions']['width'] // 10, box_data['position'][0] + box_data['dimensions']['width'] - box_data['dimensions']['width'] // 10),
                            random.randint(box_data['position'][1] + box_data['dimensions']['height'] // 10, box_data['position'][1] + box_data['dimensions']['height'] - box_data['dimensions']['height'] // 10))
                velocity_x = random.uniform(-1, 1)
                velocity_y = random.uniform(-1, 1)
                
                # Asegurar que la velocidad no sea 0 en ninguna componente o este estre -0.5 y 0.5 
                while (velocity_x < 0.5 and velocity_x > -0.5) or (velocity_y< 0.5 and velocity_y > -0.5):
                    if velocity_x < 0.5 and velocity_x > -0.5:
                        velocity_x = random.uniform(-1, 1)
                    elif velocity_y< 0.5 and velocity_y > -0.5: 
                        velocity_y= random.uniform(-1, 1)
                print(velocity_x, velocity_y)
                color = molecule_data['colorRGB']
                mass = 0
                for atom in atoms_data:
                    if atom['name'] == molecule_data['name']:
                        mass = atom['atomicMass']
                for molecule in molecules_data:
                    if molecule['name'] == molecule_data['name']:
                        mass = molecule['properties']['molecularMass']
                molecule = Molecule(molecule_data['box'], position, [velocity_x, velocity_y], color, molecule_data['radiusPx'], mass, uuid.uuid4())
                molecules.add(molecule)

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
    
    Screen.fill((0, 0, 0))
    # Dibujar las cajas
    boxes.draw(Screen)
    # Dibujar y actualizar las moléculas
    molecules.draw(Screen)

    # Renderizar y dibujar el texto de los FPS
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    Screen.blit(fps_text, (10, 10))

    pyg.display.update()
    clock.tick(60)
