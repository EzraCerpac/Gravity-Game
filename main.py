import pygame, random, os.path
from pygame.locals import *
from sys import exit

# TO DO: collisions between planets

pygame.init()
X_RES, Y_RES = 1200, 1200
SCREEN_SIZE = (X_RES, Y_RES)
screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE, 32)
clock = pygame.time.Clock()


#Game not so constants
FPS = 60
SIZE = 2
gravity_x, gravity_y = 0, 0
scroll_x, scroll_y = 0, 0
position_x, position_y = 0, 0

# Colors
BG = (23, 146, 100)

#Images
BG_LST = []
for i in range(len(os.listdir("bg"))):
    BG_LST.append(pygame.image.load(f'bg/bkgd_{i}.png').convert_alpha())

PLANET_LST = []
for i in range(49):
    file = f"planets/planet{'{:0>2}'.format(i)}.png"
    if os.path.exists(file):
        PLANET_LST.append(pygame.image.load(file).convert_alpha())


def draw_bg():
    for i, img in enumerate(BG_LST, start=1):
        scroll_con = -0.05 * i
        for x in range(-SIZE, SIZE):
            for y in range(-SIZE, SIZE):
                screen.blit(img, (int(x * img.get_width() - 500 + scroll_con * gravity_x + position_x),
                                  int(y * img.get_height() - 500 + scroll_con * gravity_y + position_y)))


class Planet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.random() / 10 + 0.025
        self.image = random.choice(PLANET_LST)
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * size), int(self.image.get_height() * size)))
        self.rect = self.image.get_rect(center=(random.randint(0, X_RES), random.randint(0, Y_RES)))

        #Intial Parameters
        self.vx, self.vy = 0, 0

    def update(self, dt):
        self.vx -= gravity_x / 1e7 * dt
        self.vy -= gravity_y / 1e7 * dt
        dx = self.vx * dt
        dy = self.vy * dt
        if self.rect.left + dx <= 0:
            dx = -self.rect.left
            self.vx *= -1
        elif self.rect.right + dx >= X_RES:
            dx = X_RES - self.rect.right
            self.vx *= -1
        if self.rect.top + dy <= 0:
            dy = -self.rect.top
            self.vy *= -1
        elif self.rect.bottom + dy >= Y_RES:
            dy = Y_RES - self.rect.bottom
            self.vy *= -1
        self.rect.x += int(dx)
        self.rect.y += int(dy)



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=1):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        type = random.randint(1, 3)
        for num in range(1, 12):
            img = pygame.image.load(f'Explosions/explosion{type}/Explosion{type}_{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.start_x = x + 0.05 * 8 * gravity_x
        self.start_y = y + 0.05 * 8 * gravity_y
        self.rect.center = (self.start_x, self.start_y)
        self.counter = 0

    def update(self):
        # scroll
        self.rect.x = -0.05 * 8 * gravity_x + position_x + self.start_x
        self.rect.y = -0.05 * 8 * gravity_y + position_y + self.start_y

        EXPLOSION_SPEED = 4
        # update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


groups = []
planet_group = pygame.sprite.Group()

explosion_group = pygame.sprite.Group()
groups.append(explosion_group)


for i in range(random.randint(10, 20)):
    planet = Planet()
    planet_group.add(planet)

groups.append(planet_group)

time = pygame.time.get_ticks()
clicked = False
running = True
while running:
    dt = pygame.time.get_ticks() - time
    time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == VIDEORESIZE:
            SCREEN_SIZE = event.size
            screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE, 32)
            pygame.display.set_caption(f"Gravity Game (resizable window, size: {event.size})")
            X_RES, Y_RES = SCREEN_SIZE
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if pygame.mouse.get_pressed()[0] and not clicked:
        clicked = True
        explosion = Explosion(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        explosion_group.add(explosion)
    elif not pygame.mouse.get_pressed()[0]:
        clicked = False

    gravity_x, gravity_y = int(X_RES / 2) - pygame.mouse.get_pos()[0], int(Y_RES / 2) - pygame.mouse.get_pos()[1]

    draw_bg()

    for group in groups:
        group.update(dt)
        group.draw(screen)

        

    pygame.display.update()
    clock.tick(FPS)


pygame.quit()

