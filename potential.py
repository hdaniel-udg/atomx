import numpy as np
import matplotlib.pyplot as plt

# Definir los nuevos parámetros del potencial de Lennard-Jones
epsilon = 1#1e-21  # Profundidad del pozo
sigma = 4#2.6e-11  # Distancia en la cual el potencial es nulo
r = np.linspace(0.8 * sigma, 3 * sigma, 1000)  # Valores de r desde 0.8*sigma hasta 3*sigma

# Calcular el potencial de Lennard-Jones
V = 4 * epsilon * ((sigma / r)**12 - (sigma / r)**6)

# Graficar el potencial
plt.figure(figsize=(8, 6))
plt.plot(r, V, label='Potencial de Lennard-Jones', color='blue')
plt.xlabel('Distancia r (m)')
plt.ylabel('Energía Potencial V(r) (J)')
plt.title('Potencial de Lennard-Jones')
plt.axhline(0, color='black', linestyle='--', linewidth=0.8)  # Línea horizontal en V=0
plt.axvline(sigma, color='red', linestyle='--', linewidth=0.8, label='Distancia de equilibrio σ')  # Línea vertical en r=σ
plt.legend()
plt.grid(True)
plt.show()
