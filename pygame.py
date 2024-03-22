import pygame as pyg
import sys
import json
import random
import math

kBoltzman = 1.380649e-23  # 10-23 J K-1
scale = 0.0


class Box(pyg.sprite.Sprite):
    def __init__(self, name, position, dimensions, backgroundColor, block, temperature):
        super().__init__()
        self.name = name
        self.temperature = temperature
        self.block = block
        self.rect = pyg.Rect(position[0], position[1], dimensions['width'], dimensions['height'])
        self.image = pyg.Surface((self.rect.width, self.rect.height))
        pyg.draw.rect(self.image, backgroundColor, self.image.get_rect(), width=1)  # Dibujamos el borde

    def createMolecules(self, conditionData):
        molecules = pyg.sprite.Group()
        for moleculeData in conditionData:
            if moleculeData['box'] == self.name and moleculeData['number'] != 0:
                positions = []
                velocities = []
                for _ in range(moleculeData['number']):
                    position = (random.randint(self.rect.left + (self.rect.left * 0.03),
                                               self.rect.right - (self.rect.right * 0.03)),
                                random.randint(self.rect.top + (self.rect.top * 0.03),
                                               self.rect.bottom - (self.rect.bottom * 0.03)))
                    positions.append(position)
                mass = 0
                for atom in atomsData:
                    if atom['name'] == moleculeData['name']:
                        mass = atom['atomicMass']
                        break

                # Generar la lista de sublistas para las partículas
                listaParticulas = [self.generarSublista() for _ in range(moleculeData['number'])]
                # Calcular la magnitud de cada velocidad en las partículas originales
                magnitudes = [math.sqrt(particula[0] ** 2 + particula[1] ** 2) for particula in listaParticulas]
                # Calcular la velocidad promedio original
                velocidadPromedioOriginal = sum(magnitudes) / moleculeData['number']
                # Definir la nueva velocidad promedio objetivo
                velocidadPromedioObjetivo = math.sqrt((kBoltzman * self.temperature) / mass)
                # Ajustar la velocidad promedio al valor objetivo
                factorAjuste = velocidadPromedioObjetivo / velocidadPromedioOriginal
                # Aplicar el factor de ajuste a cada velocidad en las partículas
                velocities = [[particula[0] * factorAjuste, particula[1] * factorAjuste] for particula in
                              listaParticulas]
                for i in range(moleculeData['number']):
                    molecule = Molecule(moleculeData['box'], positions[i], velocities[i], moleculeData['colorRGB'],
                                        int(moleculeData['radiusNm'] // 0.1), mass, pyg.math.Vector2(0, 0))
                    molecules.add(molecule)
        return molecules

    # Función para generar una sublista con dos números aleatorios entre -5 y 5
    def generarSublista(self):
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        return [x, y]


class Molecule(pyg.sprite.Sprite):
    def __init__(self, boxName, position, velocity, color, length, mass, acceleration):
        super().__init__()
        self.boxName = boxName
        self.mass = mass
        self.rect = pyg.Rect(position[0], position[1], length, length)
        self.image = pyg.Surface((length, length), pyg.SRCALPHA)
        pyg.draw.rect(self.image, color, self.image.get_rect(), width=0)  # Dibujamos un cuadrado sólido
        self.velocity = velocity
        self.acceleration = acceleration

    def update(self):
        if not paused:  # Solo actualiza si no está pausado
            # Colisión con los bordes de la pantalla
            if self.rect.left <= 0 or self.rect.right >= screenWidth:
                self.velocity[0] *= -1
            if self.rect.top <= 0 or self.rect.bottom >= screenHeight:
                self.velocity[1] *= -1

            # Colisión con las cajas
            for box in boxes:
                if box.block and self.rect.colliderect(box.rect):
                    if self.rect.left <= box.rect.left or self.rect.right >= box.rect.right:
                        self.velocity[0] *= -1
                    if self.rect.top <= box.rect.top or self.rect.bottom >= box.rect.bottom:
                        self.velocity[1] *= -1

            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]

    def getMagnitude(self):
        return math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)


pyg.init()
Screen = pyg.display.set_mode((800, 600), pyg.RESIZABLE)
pyg.display.set_caption('Atomx')
screenWidth, screenHeight = Screen.get_size()

with open('settings/initialCondition.json') as conditionJson:
    conditionData = json.load(conditionJson)

with open('settings/molecules.json') as moleculesJson:
    moleculesData = json.load(moleculesJson)

with open('settings/atoms.json') as atomsJson:
    atomsData = json.load(atomsJson)

with open('settings/boxes.json') as boxesJson:
    boxesData = json.load(boxesJson)

boxes = pyg.sprite.Group()
molecules = pyg.sprite.Group()
for boxData in boxesData:
    backgroundColor = boxData['backgroundColorRGB']
    if not boxData['display']:
        backgroundColor = (0, 0, 0)
    box = Box(boxData['name'], boxData['position'], boxData['dimensions'], backgroundColor, boxData['block'],
              boxData['temperature'])
    molecules.add(box.createMolecules(conditionData))
    boxes.add(box)

clock = pyg.time.Clock()
paused = False  # Variable para controlar el estado de pausa

while True:
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            pyg.quit()
            sys.exit()
        elif event.type == pyg.VIDEORESIZE:
            width, height = event.size
            Screen = pyg.display.set_mode((width, height), pyg.RESIZABLE)
            screenWidth, screenHeight = Screen.get_size()
        elif event.type == pyg.KEYDOWN:
            if event.key == pyg.K_SPACE:
                paused = not paused  # Cambiar el estado de pausa

    molecules.update()

    Screen.fill((0, 0, 0))
    boxes.draw(Screen)
    molecules.draw(Screen)

    for box in boxes:
        velocity = 0
        mass = 0
        count = 0
        for molecule in molecules:
            if box.rect.colliderect(molecule.rect):
                velocity += molecule.getMagnitude()
                mass += molecule.mass
                count += 1
        averageVelocity = velocity / count if count != 0 else 0
        averageMass = mass / count if count != 0 else 0
        temperatureCalculated = (0.5 * averageMass * averageVelocity ** 2) / kBoltzman

        details = f"Temperatura: {temperatureCalculated:.3f} K\nVelocidad Promedio: {averageVelocity:.2f} m/s"
        details_lines = details.split('\n')

        line_height = 20
        y_position = box.rect.y - 20
        for line in details_lines:
            details_screen = pyg.font.Font(None, 17).render(line, True, (255, 255, 255))
            Screen.blit(details_screen, (box.rect.x, y_position))
            y_position -= line_height

    pyg.display.update()
    clock.tick(60)
