import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import random
import json
from scipy.constants import k as kBoltzman
import math

sigma =3.3e-10
epsilon = 43e-23

def potentialLennarJones(posi, posj):
    # Calcular la distancia entre las partículas
    dx = posi[0] - posj[0]
    dy = posi[1] - posj[1]
    distance = np.sqrt(dx ** 2 + dy ** 2)
    # Calcular el potencial de Lennard-Jones
    if distance != 0:
        fx = -24*epsilon*dx*(((2*sigma**12)/distance**14) - (sigma**6/distance**8))
        fy = -24*epsilon*dy*(((2*sigma**12)/distance**14) - (sigma**6/distance**8))
    else:
        fx = float('inf')  # Evitar división por cero
        fy = float('inf')
    force = [fx,fy]
    #print('Distancia:',distance)
    return force

# Función para generar una sublista con dos números aleatorios entre -5 y 5, está funcion sirve para general las 
# velocidades aleatorias respectivas a cada atomo
def generateSublist():
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)
    return [x, y]


def generateVelocities(initial, uniqueMass):
    velocities = []
    if initial['number'] != 0:
        # Generar la lista de sublistas para las partículas
        listaParticulas = [generateSublist() for _ in range(initial['number'])]
        # Calcular la magnitud de cada velocidad en las partículas originales
        magnitudes = [math.sqrt(particula[0] ** 2 + particula[1] ** 2) for particula in listaParticulas]
        # Calcular la velocidad promedio original
        velocidadPromedioOriginal = sum(magnitudes) / initial['number']
        # Definir la nueva velocidad promedio objetivo
        velocidadPromedioObjetivo = math.sqrt(( kBoltzman * initial['temperature']) / uniqueMass)
        # Ajustar la velocidad promedio al valor objetivo
        factorAjuste = velocidadPromedioObjetivo / velocidadPromedioOriginal
        # Aplicar el factor de ajuste a cada velocidad en las partículas
        velocities = [[particula[0] * factorAjuste, particula[1] * factorAjuste] for particula in listaParticulas]
    return velocities


# Función para manejar el evento de zoom al presionar las flechas hacia arriba y hacia abajo
def on_key(event):
    if event.key == 'up':
        ax.set_xlim(ax.get_xlim()[0] * 0.9, ax.get_xlim()[1] * 0.9)
        ax.set_ylim(ax.get_ylim()[0] * 0.9, ax.get_ylim()[1] * 0.9)
        plt.draw()
    elif event.key == 'down':
        ax.set_xlim(ax.get_xlim()[0] * 1.1, ax.get_xlim()[1] * 1.1)
        ax.set_ylim(ax.get_ylim()[0] * 1.1, ax.get_ylim()[1] * 1.1)
        plt.draw()

# Crear la figura y los ejes
fig, ax = plt.subplots()
ax.set_xlim(-0.5e-8, 0.5e-8)
ax.set_ylim(-0.5e-8, 0.5e-8)
# Crear el texto para mostrar el tiempo transcurrido
tiempoTranscurrido = 0
timeText = ax.text(0.05, 0.95, f'Tiempo transcurrido: {tiempoTranscurrido} segundos', transform=ax.transAxes, color='white', fontsize=11)

# Función de animación para actualizar la posición de las bolitas y gestionar el rebote
def update(frame):
    global tiempoTranscurrido
    tiempoTranscurridoAnterior = tiempoTranscurrido
    tiempoTranscurrido += 1 * speedAnimation
    dynamicMolecules = []
    for i in range(len(molecules)):
        posx_i, posy_i = molecules[i].center  # Obtener la posición particula i
        #posx, posy= molecules[i].center
        posi = [posx_i, posy_i]
        forces = []
        for j in range(len(molecules)):
            #No toma las interacciones entre si misma
            if i != j:
                #print(i,j)
                posx_j, posy_j = molecules[j].center  # Obtener la posición particula i
                posj = [posx_j,posy_j]
                forces.append(potentialLennarJones(posi, posj))
        forces = np.array(forces)
        if len(forces)!=0:
            Force = [np.sum(forces[:,0]), np.sum(forces[:,1])]
            acx=Force[0]/moleculesMass[i]
            acy=Force[1]/moleculesMass[i]
            #print(forces)   
            #print(acx,acy)
        dynamicMolecules.append([Force[0], Force[1],acx, acy])
    for i in range(len(molecules)):
        dt = (tiempoTranscurrido-tiempoTranscurridoAnterior)
        vx0, vy0 = molecule_velocities[i]  # Obtener la velocidad de la molécula
        vxf = vx0 + dynamicMolecules[i][2]*dt
        vyf = vy0 + dynamicMolecules[i][3]*dt

        #print(i)
        #print('x: ',vxf)
        #print('y:',vyf)
        #print('Fuerza:', dynamicMolecules[i][0],dynamicMolecules[i][1])
        #print('Aceleracion:', dynamicMolecules[i][2],dynamicMolecules[i][3])
        
        posx0, posy0 = molecules[i].center 
        posxf = posx0 + vx0*dt + 0.5*dynamicMolecules[i][2]*dt**2
        posyf = posy0 + vy0*dt + 0.5*dynamicMolecules[i][3]*dt**2
        
        # Aplicar condiciones periódicas de contorno en el eje x
        if posxf + molecules[i].radius >= box_width / 2:
            posxf -= box_width
        elif posxf - molecules[i].radius <= -box_width / 2:
            posxf += box_width

        # Aplicar condiciones periódicas de contorno en el eje y
        if posyf + molecules[i].radius >= box_height / 2:
            posyf -= box_height
        elif posyf - molecules[i].radius <= -box_height / 2:
            posyf += box_height
        print(molecules[i], len(molecules))
        molecules[i].center = (posxf, posyf)  # Actualizar posición de la molécula
        molecule_velocities[i] = [vxf, vyf]  # Actualizar velocidad en la lista de velocidades
    # Actualizar el texto que muestra el tiempo transcurrido
    timeText.set_text(f'Time : {tiempoTranscurrido} segundos')
    #time.sleep(5)
    return molecules

with open('settings/initial.json') as conditionJson:
    conditionData = json.load(conditionJson)


with open('settings/atoms.json', encoding='utf-8') as atomsJson:
    atomsData = json.load(atomsJson)

molecules = []
moleculesMass = []
molecule_velocities = []  # Lista para almacenar velocidades iniciales
for initial in conditionData:
    velocities = []
    tooMany = []
    tooMany.append(False)
    count = 1
    mass = 0
    for atom in atomsData:
        if atom['name'] == initial['name']:
            mass = atom['atomicMass']
            break
    if mass != 0:
        velocities = generateVelocities(initial, uniqueMass=mass)
    for i in range(initial['number']):
        radius = initial['radius']
        color = initial['color']
        box_width, box_height = initial['boxDimensions']
        attempt = 0
        while True:
            posx = random.uniform((-box_width / 2) * 0.90, (box_width / 2) * 0.90)
            posy = random.uniform((-box_height / 2) * 0.90, (box_height / 2) * 0.90)
            valid_position = True
            for existing_molecule in molecules:
                dx = existing_molecule.center[0] - posx
                dy = existing_molecule.center[1] - posy
                distance = np.sqrt(dx ** 2 + dy ** 2)
                if distance < (existing_molecule.radius + radius):
                    valid_position = False
                    break
            if valid_position:
                attempt = 0  # Reiniciar attempt solo si se encuentra una posición válida
                break
            if (attempt > 1000):
                tooMany.append(True)
                count += 1
                break
            else:
                attempt += 1
        molecule = plt.Circle((posx, posy), radius, fc=color)
        ax.add_patch(molecule)
        molecules.append(molecule)
        moleculesMass.append(mass)
        # Asignar velocidad aleatoria a la molécula
        if len(velocities)!=0:
            vx = velocities[i][0]
            vy = velocities[i][1]
        molecule_velocities.append([vx, vy])
    if any(tooMany):
        print('Too many molecules :c just: ', count)

# Vincular el evento de teclado a la función de zoom
plt.connect('key_press_event', on_key)

# Crear la animación con intervalo y fps ajustados
speedAnimation = 2e-15
ani = FuncAnimation(fig, update, frames=None, interval=0.0001, cache_frame_data=False)

# Cambiar el color del fondo dentro de los ejes a negro
ax.set_facecolor('black')

# Guardar la animación como archivo de video
#ani.save('animation40K1e-15dt120fps.mp4', fps=120, extra_args=['-vcodec', 'libx264'])

# Mostrar la animación
plt.xlabel('Distancia (m)')
plt.ylabel('Distancia (m)')
plt.grid(color='dimgray')
plt.show()