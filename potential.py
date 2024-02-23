import pygame as pyg
import sys
import random
import math

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Parámetros de la ventana
WIDTH, HEIGHT = 800, 600
FPS = 60

class Ball(pyg.sprite.Sprite):
    def __init__(self, x, y, radius, color, velocity):
        super().__init__()
        self.radius = radius
        self.color = color
        self.velocity = velocity
        self.image = pyg.Surface((radius * 2, radius * 2), pyg.SRCALPHA)
        pyg.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Rebotar en los bordes de la ventana
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.velocity[0] *= -1
        if self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.velocity[1] *= -1

        # Manejar colisiones entre esferas
        for ball in balls:
            if ball != self:
                if pyg.sprite.collide_circle(self, ball):
                    dx = self.rect.x - ball.rect.x
                    dy = self.rect.y - ball.rect.y
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    if distance < self.radius + ball.radius:
                        angle = math.atan2(dy, dx)
                        target_x = self.rect.x + math.cos(angle) * (self.radius + ball.radius - distance + 1)
                        target_y = self.rect.y + math.sin(angle) * (self.radius + ball.radius - distance + 1)
                        self.rect.x = target_x
                        self.rect.y = target_y
                        self.velocity[0] *= -1
                        self.velocity[1] *= -1
                        ball.velocity[0] *= -1
                        ball.velocity[1] *= -1

# Inicializar Pygame
pyg.init()
screen = pyg.display.set_mode((WIDTH, HEIGHT))
pyg.display.set_caption('Esferas Colisionando')
clock = pyg.time.Clock()

# Grupo de esferas
balls = pyg.sprite.Group()

# Crear esferas aleatorias
for _ in range(10):
    radius = random.randint(20, 40)
    x = random.randint(radius, WIDTH - radius)
    y = random.randint(radius, HEIGHT - radius)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    velocity = [random.randint(-5, 5), random.randint(-5, 5)]
    ball = Ball(x, y, radius, color, velocity)
    balls.add(ball)

# Bucle principal del juego
running = True
while running:
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False

    # Actualizar esferas
    balls.update()

    # Dibujar
    screen.fill(BLACK)
    balls.draw(screen)
    pyg.display.flip()

    # Esperar al siguiente fotograma
    clock.tick(FPS)

pyg.quit()
sys.exit()
