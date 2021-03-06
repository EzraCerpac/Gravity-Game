import pygame, random, os.path, shelve
from pygame.locals import *
from math import sin, cos, radians
from sys import exit
from time import sleep

# TO DO: collisions between planets

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("Sound/spaceinvaders1.mpeg")
pygame.mixer.music.play(-1)
X_RES, Y_RES = 1200, 1200
SCREEN_SIZE = (X_RES, Y_RES)
screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE, 32)
clock = pygame.time.Clock()

# Game not so constants
FPS = 30
SIZE = 2
gravity_x, gravity_y = 0, 0
scroll_x, scroll_y = 0, 0
position_x, position_y = 0, 0
score = 0
try:
    with shelve.open("highscore") as r:
        high_score = r['high_score']
except:
    high_score = 0

# Colors
BG = (23, 146, 100)

# Define font
font = pygame.font.SysFont('Futura', 30)

# Sound Effects
DEADSFX = pygame.mixer.Sound("Sound/mixkit-arcade-space-shooter-dead-notification-272.wav")
CRYSTALSFX = pygame.mixer.Sound("Sound/mixkit-quick-positive-video-game-notification-interface-265.wav")
HSCORESFX = pygame.mixer.Sound("Sound/mixkit-completion-of-a-level-2063.wav")

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Images
BG_LST = []
for i in range(len(os.listdir("bg"))):
    BG_LST.append(pygame.image.load(f'bg/bkgd_{i}.png').convert_alpha())

PLANET_LST = []
for i in range(49):
    file = f"planets/planet{'{:0>2}'.format(i)}.png"
    if os.path.exists(file):
        PLANET_LST.append(pygame.image.load(file).convert_alpha())

CRISTAL_LST = [pygame.transform.scale(pygame.image.load(f"cristals/{x + 1}.png").convert_alpha(), (40, 40))
               for x in range(len(os.listdir("cristals")))]

N_EXHAUST_LST = []
T_EXHAUST_LST = []
for i in range(4):
    N_EXHAUST_LST.append(pygame.transform.scale2x(pygame.image.load(f"Ship/Exhaust/Normal_flight/Exhaust1/exhaust{i+1}.png")).convert_alpha())
    T_EXHAUST_LST.append(pygame.transform.scale2x(pygame.image.load(f"Ship/Exhaust/Turbo_flight/Exhaust1/exhaust{i+1}.png")).convert_alpha())

RESTART_BUTTON = pygame.image.load("Buttons/restart.png").convert_alpha()


def restart():
    global dead, score, new_high_score, player
    dead = False
    score = 0
    new_high_score = False
    cristal_group.empty()
    for i in range(random.randint(5, 10)):
        cristal = Cristal((random.randint(0, X_RES), random.randint(0, Y_RES)))
        cristal_group.add(cristal)
    player = Ship()
    player_group.add(player)
    explosion = Explosion(player.rect.centerx, player.rect.centery, 4)
    explosion_group.add(explosion)


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


def quit_game():
    # Save thing
    with shelve.open("highscore") as w:
        w['high_score'] = high_score

    # Music Fade
    fade_time = 3     # s
    pygame.mixer.music.fadeout(int(fade_time * 1000))

    # Screen Fade
    fade_rect = pygame.display.get_surface().get_rect()
    fade_surf = pygame.Surface(fade_rect.size, flags=pygame.SRCALPHA)
    for alpha in range(256):
        fade_surf.fill((0, 0, 0, alpha))
        screen.blit(fade_surf, fade_rect)
        pygame.display.update()
        sleep(fade_time / 100)

    # quit
    pygame.quit()
    exit()

class Ship(pygame.sprite.Sprite):
    def __init__(self, position: tuple = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)):
        super().__init__()
        self.master_image = pygame.image.load("Ship/Ship6.png").convert_alpha()
        self.angle = 0
        self.image, self.rect = rotate(self.master_image, self.angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = position
        self.max_speed = 0.25
        self.turn_speed = 0.1
        self.acceleration = .0001

        # initial exhaust
        self.exhaust_index = 0
        self.exhaust_img, self.exhaust_rect = rotate(T_EXHAUST_LST[self.exhaust_index], self.angle)

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
        self.speed_vector = pygame.math.Vector2(self.speed * cos(-radians(self.angle)),
                                                self.speed * sin(-radians(self.angle)))
        self.position_vector += self.speed_vector * dt
        self.image, self.rect = rotate(self.master_image, self.angle)
        self.mask = pygame.mask.from_surface(self.image)

        #Screen boundry
        if self.position_vector[0] - self.image.get_width() / 2 <= 0:
            self.position_vector[0] = self.image.get_width() // 2
        elif self.position_vector[0] + self.image.get_width() / 2 >= SCREEN_SIZE[0]:
            self.position_vector[0] = SCREEN_SIZE[0] - self.image.get_width() // 2
        if self.position_vector[1] - self.image.get_height() / 2 <= 0:
            self.position_vector[1] = self.image.get_height() // 2
        elif self.position_vector[1] + self.image.get_height() / 2 >= SCREEN_SIZE[1]:
            self.position_vector[1] = SCREEN_SIZE[1] - self.image.get_height() // 2

        self.rect.center = self.position_vector

        self.draw_exhaust()

        self.check_score()
        if not self.invincible:
            self.check_dead()
        else:
            draw_text("Protected", font, "white", self.rect.centerx - 60, self.rect.centery - 80)

    def check_score(self):
        global score, high_score, new_high_score
        for cristal in pygame.sprite.spritecollide(self, cristal_group, True, pygame.sprite.collide_mask):
            score += 1
            CRYSTALSFX.play()
            if score > high_score:
                high_score = score
                new_high_score = True
            twinkel = Explosion(cristal.rect.centerx, cristal.rect.centery, 0.5)
            twinkel_group.add(twinkel)

    def check_dead(self):
        global dead
        if pygame.sprite.spritecollide(self, planet_group, False, pygame.sprite.collide_mask):
            dead = True
            DEADSFX.play()
            boom = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(boom)
            self.kill()

    def draw_exhaust(self):
        self.exhaust_index += self.speed
        if self.exhaust_index >= len(T_EXHAUST_LST):
            self.exhaust_index = 0

        if self.speed >= self.max_speed - 0.01:
            self.exhaust_img, self.exhaust_rect = rotate(T_EXHAUST_LST[int(self.exhaust_index)], self.angle)
        elif 0.01 < self.speed:
            self.exhaust_img, self.exhaust_rect = rotate(N_EXHAUST_LST[int(self.exhaust_index)], self.angle)
        else:
            return None

        dist = 70
        self.exhaust_rect.center = (self.rect.centerx - dist * cos(-radians(self.angle)),
                                    self.rect.centery - dist * sin(-radians(self.angle)))

        screen.blit(self.exhaust_img, self.exhaust_rect)


class Cristal(pygame.sprite.Sprite):
    def __init__(self, position: tuple):
        super().__init__()
        self.image = random.choice(CRISTAL_LST)
        self.rect = self.image.get_rect(center=position)
        self.mask = pygame.mask.from_surface(self.image)


class Planet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.random() / 2.5 + 0.1
        self.image = random.choice(PLANET_LST)
        self.image = pygame.transform.scale(self.image,
                                            (int(self.image.get_width() * size), int(self.image.get_height() * size)))
        self.rect = self.image.get_rect(center=(random.randint(0, X_RES), random.randint(0, Y_RES)))
        self.mask = pygame.mask.from_surface(self.image)
        self.vector = pygame.math.Vector2(self.rect.center)
        self.radius = self.rect.width // 2

        # Initial Parameters
        self.vx, self.vy = random.gauss(0, 0.07), random.gauss(0, 0.08)

    def update(self, dt):
        self.vx -= gravity_x / 1e7 * dt
        self.vy -= gravity_y / 1e7 * dt
        dx = self.vx * dt
        dy = self.vy * dt

        # Wall colission
        damping = 0.95
        if self.rect.left + dx <= 0:
            dx = -self.rect.left
            self.vx *= -1 * damping
        elif self.rect.right + dx >= X_RES:
            dx = X_RES - self.rect.right
            self.vx *= -1 * damping
        if self.rect.top + dy <= 0:
            dy = -self.rect.top
            self.vy *= -1 * damping
        elif self.rect.bottom + dy >= Y_RES:
            dy = Y_RES - self.rect.bottom
            self.vy *= -1 * damping

        self.rect.x += int(dx)
        self.rect.y += int(dy)

        # collisions
        self.vector = pygame.math.Vector2(self.rect.center)
        for plan in planet_group:
            if plan is not self:
                if self.vector.distance_to(plan.vector) < (self.radius + plan.radius) * 1.01:
                    self.rect.x -= 1.01 * int(dx)
                    self.rect.y -= 1.01 * int(dy)
                    nv = plan.vector - self.vector
                    if nv:
                        m1 = pygame.math.Vector2(self.vx, self.vy).reflect(nv)
                        m2 = pygame.math.Vector2(plan.vx, plan.vy).reflect(nv)
                        self.vx, self.vy = m1.x, m1.y
                        plan.vx, plan.vy = m2.x, m2.y
                    else:
                        self.vx *= -1
                        self.vy *= -1
                    # self.rect.x += self.vx * dt
                    # self.rect.y += self.vy * dt


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
        self.start_x = x  # + 0.05 * 8 * gravity_x
        self.start_y = y  # + 0.05 * 8 * gravity_y
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

player = Ship()
player_group = pygame.sprite.GroupSingle(player)

# Spawn planets
for i in range(random.randint(8, 15)):
    planet = Planet()
    if not pygame.sprite.spritecollideany(planet, planet_group):
        planet_group.add(planet)
groups.append(planet_group)

# Spawn starting cristals
for i in range(random.randint(5, 10)):
    cristal = Cristal((random.randint(0, X_RES), random.randint(0, Y_RES)))
    cristal_group.add(cristal)
groups.append(cristal_group)

# Event creation
CRISTAL_EVENT = pygame.USEREVENT + 1
INVINCIBLE_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(CRISTAL_EVENT, 3000)
pygame.time.set_timer(INVINCIBLE_EVENT, 7000)

time = pygame.time.get_ticks()
new_high_score = False
dead = False
clicked = False
while True:
    dt = pygame.time.get_ticks() - time
    time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
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
                quit_game()
            if event.key == pygame.K_r:
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
    explosion_group.update()
    cristal_group.draw(screen)
    twinkel_group.draw(screen)
    planet_group.draw(screen)
    player_group.update(dt)
    player_group.draw(screen)
    explosion_group.draw(screen)
    draw_text(f"Score: {score}", font, "white", 10, 10)

    if dead:
        if new_high_score:
            # HSCORESFX.play()
            draw_text(f"NEW HIGHSCORE!", font, "white", SCREEN_SIZE[0] // 2 - 130, SCREEN_SIZE[1] // 2 - 260)
        draw_text(f"Highscore: {high_score}", font, "white", SCREEN_SIZE[0] // 2 - 80, SCREEN_SIZE[1] // 2 - 180)
        button = Button(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2, RESTART_BUTTON, 1)
        if button.draw(screen):
            restart()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
