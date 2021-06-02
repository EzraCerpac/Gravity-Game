import pygame, random, os.path
from pygame.locals import *
from math import sin, cos, radians
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
score = 0

# Colors
BG = (23, 146, 100)

#define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#Images
BG_LST = []
for i in range(len(os.listdir("bg"))):
    BG_LST.append(pygame.image.load(f'bg/bkgd_{i}.png').convert_alpha())

PLANET_LST = []
for i in range(49):
    file = f"planets/planet{'{:0>2}'.format(i)}.png"
    if os.path.exists(file):
        PLANET_LST.append(pygame.image.load(file).convert_alpha())

CRISTAL_LST = [pygame.transform.scale(pygame.image.load(f"cristals/{x+1}.png").convert_alpha(), (40, 40))
               for x in range(len(os.listdir("cristals")))]

RESTART_BUTTON = pygame.image.load("Buttons/restart.png").convert_alpha().set_colorkey((252, 253, 255))

def restart():
    global dead, score
    dead = False
    score = 0
    cristal_group.empty()
    for i in range(random.randint(5, 10)):
        cristal = Cristal((random.randint(0, X_RES), random.randint(0, Y_RES)))
        planet_group.add(cristal)
    groups.append(cristal_group)
    player = Ship()
    player_group.add(player)

def rotate(surface, angle):
    rotated_surface = pygame.transform.rotozoom(surface, angle, 1)
    rotated_rect = rotated_surface.get_rect(center=(surface.get_width() / 2, surface.get_height() / 2))
    return rotated_surface, rotated_rect


def draw_bg():
    for i, img in enumerate(BG_LST, start=1):
        scroll_con = -0.05 * i
        for x in range(-SIZE, SIZE):
            for y in range(-SIZE, SIZE):
                screen.blit(img, (int(x * img.get_width() - 500 + scroll_con * gravity_x + position_x),
                                  int(y * img.get_height() - 500 + scroll_con * gravity_y + position_y)))

class Ship(pygame.sprite.Sprite):
    def __init__(self, position: tuple = (SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2)):
        super().__init__()
        self.master_image = pygame.image.load("Ship/Ship6.png").convert_alpha()
        #self.rect = self.master_image.get_rect(center=[x // 2 for x in SCREEN_SIZE])
        self.angle = 0
        self.image, self.rect = rotate(self.master_image, self.angle)
        self.rect.center = position
        self.max_speed = 0.2
        self.turn_speed = 0.1
        self.acceleration = .0001

        # initial parameters
        self.invincible = True
        self.position_vector = pygame.math.Vector2(self.rect.center)
        self.speed = 0
        self.acceleration_sign = 0
        self.turn_dir = 0
        self.speed_vector = pygame.math.Vector2(self.speed * sin(self.angle), self.speed * cos(self.angle))

    def update(self, dt):
        self.angle += self.turn_speed * self.turn_dir * dt
        self.speed += self.acceleration * self.acceleration_sign * dt
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        elif self.speed < 0:
            self.speed = 0
        self.speed_vector = pygame.math.Vector2(self.speed * cos(-radians(self.angle)), self.speed * sin(-radians(self.angle)))
        self.position_vector += self.speed_vector * dt
        self.image, self.rect = rotate(self.master_image, self.angle)
        self.rect.center = self.position_vector
        self.check_score()
        if not self.invincible:
            self.check_dead()

    def check_score(self):
        global score
        for cristal in cristal_group:
            if self.rect.colliderect(cristal.rect):
                score += 1
                twinkel = Explosion(cristal.rect.centerx, cristal.rect.centery, 0.5)
                twinkel_group.add(twinkel)
                cristal.kill()
                print(score)

    def check_dead(self):
        global dead
        if pygame.sprite.spritecollide(self, planet_group, False, pygame.sprite.collide_mask):
            dead = True
            boom = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(boom)
            self.kill()

class Cristal(pygame.sprite.Sprite):
    def __init__(self, position: tuple):
        super().__init__()
        self.image = random.choice(CRISTAL_LST)
        self.rect = self.image.get_rect(center=position)

class Planet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.random() / 10 + 0.025
        self.image = random.choice(PLANET_LST)
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * size), int(self.image.get_height() * size)))
        self.rect = self.image.get_rect(center=(random.randint(0, X_RES), random.randint(0, Y_RES)))
        self.mask = pygame.mask.from_surface(self.image)
        self.vector = pygame.math.Vector2(self.rect.center)
        self.radius = self.rect.width // 2

        #Intial Parameters
        self.vx, self.vy = random.gauss(0, 0.08), random.gauss(0, 0.08)

    def update(self, dt):
        self.vx -= gravity_x / 1e6 * dt
        self.vy -= gravity_y / 1e6 * dt
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

        # collisions
        # for plan in planet_group:
        #     if self.vector.distance_to(plan.vector) < self.radius + plan.radius and plan is not self:
        #         print("hit")
        #         nv = plan.vector - self.vector
        #         m1 = pygame.math.Vector2(self.vx, self.vy).reflect(nv)
        #         m2 = pygame.math.Vector2(plan.vx, plan.vy).reflect(nv)
        #         self.vx, self.vy = m1.x, m1.y
        #         plan.vx, plan.vy = m2.x, m2.y



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
        self.start_x = x# + 0.05 * 8 * gravity_x
        self.start_y = y# + 0.05 * 8 * gravity_y
        self.rect.center = (self.start_x, self.start_y)
        self.counter = 0

    def update(self):
        # scroll
        # self.rect.x = -0.05 * 8 * gravity_x + position_x + self.start_x
        # self.rect.y = -0.05 * 8 * gravity_y + position_y + self.start_y

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


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                action = True
                self.clicked = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


# Groups
groups = []
planet_group = pygame.sprite.Group()
cristal_group = pygame.sprite.Group()
twinkel_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
groups.append(explosion_group)

player_group = pygame.sprite.GroupSingle()
player = Ship()
player_group.add(player)

# Spawn planets
for i in range(random.randint(8, 15)):
    planet = Planet()
    planet_group.add(planet)
groups.append(planet_group)

# Spawn starting cristals
for i in range(random.randint(5, 10)):
    cristal = Cristal((random.randint(0, X_RES), random.randint(0, Y_RES)))
    planet_group.add(cristal)
groups.append(cristal_group)

# Event creation
CRISTAL_EVENT = pygame.USEREVENT + 1
INVINCIBLE_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(CRISTAL_EVENT, 3000)
pygame.time.set_timer(INVINCIBLE_EVENT, 7000)

time = pygame.time.get_ticks()
dead = False
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
        elif event.type == CRISTAL_EVENT:
            cristal = Cristal((random.randint(0, X_RES), random.randint(0, Y_RES)))
            cristal_group.add(cristal)
        elif event.type == INVINCIBLE_EVENT:
            player.invincible = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if dead and event.key == pygame.K_r:
                restart()
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                player.turn_dir += 1
            if event.key in [pygame.K_RIGHT, pygame.K_d]:
                player.turn_dir -= 1
            if event.key in [pygame.K_UP, pygame.K_w]:
                player.acceleration_sign += 1
            if event.key in [pygame.K_DOWN, pygame.K_s]:
                player.acceleration_sign -= 1
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                player.turn_dir -= 1
            if event.key in [pygame.K_RIGHT, pygame.K_d]:
                player.turn_dir += 1
            if event.key in [pygame.K_UP, pygame.K_w]:
                player.acceleration_sign -= 1
            if event.key in [pygame.K_DOWN, pygame.K_s]:
                player.acceleration_sign += 1

    if pygame.mouse.get_pressed()[0] and not clicked:
        clicked = True
        explosion = Explosion(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        explosion_group.add(explosion)
    elif not pygame.mouse.get_pressed()[0]:
        clicked = False

    gravity_x, gravity_y = int(X_RES / 2) - pygame.mouse.get_pos()[0], int(Y_RES / 2) - pygame.mouse.get_pos()[1]

    draw_bg()

    twinkel_group.update()
    planet_group.update(dt)
    player_group.update(dt)
    explosion_group.update()
    cristal_group.draw(screen)
    twinkel_group.draw(screen)
    player_group.draw(screen)
    planet_group.draw(screen)
    explosion_group.draw(screen)
    draw_text(f"Score: {score}", font, "white", 10, 10)

    if dead:
        button = Button(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2,
                        RESTART_BUTTON, 1)
        if button.draw(screen):
            restart()

    pygame.display.update()
    clock.tick(FPS)


pygame.quit()

