import pygame, sys, random, json
from pygame.locals import *

screen_width, screen_height = 1542, 880
screen = pygame.display.set_mode((screen_width, screen_height))
fps = pygame.time.Clock()
GROUND_LEVEL = 700
GRAVITY = 4

class stars(pygame.sprite.Sprite):
    def __init__(self,x):
        super(stars,self).__init__()
        self.image = pygame.Surface((1,1))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (screen_width,x))
    def update(self):
        self.rect.x -= 4

class ground(pygame.sprite.Sprite):
    def __init__(self,gd_locx,gd_locy,gd_sizex,gd_sizey):
        super(ground,self).__init__()
        self.image = pygame.Surface((gd_sizex, gd_sizey))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(midleft = (gd_locx,gd_locy))
    def update(self, pressed_keys):
        if pressed_keys[K_d]:
            self.rect.x -= 5
        if pressed_keys[K_a]:
            self.rect.x += 5

class Player(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.Surface((50,50))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (140,50))
        self.jump_vel = 40
        self.gravitystate = False
    def update(self, pressed_keys):
        global GRAVITY, player_gdcollisions
        if self.gravitystate:
            self.rect.y -= self.jump_vel
            if self.jump_vel <= -30:
                self.jump_vel = -30
            else:
                self.jump_vel -= 3
        player_gdcollisions = pygame.sprite.spritecollide(player, ground_group, dokill = False, collided = None)
        print (player_gdcollisions)
        for x in player_gdcollisions:
            if abs(self.rect.bottom-x.rect.top) <= 20:
                self.rect.bottom = x.rect.top + 1
                self.jump_vel = 40
                self.gravitystate = False
                GRAVITY = 4
            if abs(self.rect.left-x.rect.right) <= 20:
                self.rect.left = x.rect.right
            if abs(self.rect.right-x.rect.left) <= 20:
                self.rect.right = x.rect.left
            if abs(self.rect.top-x.rect.bottom) <= 30:
                self.rect.top = x.rect.bottom
                self.jump_vel = 40
                self.gravitystate = False
        if not player_gdcollisions and self.gravitystate == False:
            self.rect.y += GRAVITY
            GRAVITY += 4
            if GRAVITY >= 30:
                GRAVITY = 30
    def player_pos(self):
        return self.rect.center

player = Player()


stars_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()
stars_timer = 0

ground_group.add(ground(0,GROUND_LEVEL,700,300))
ground_group.add(ground(300,450,200,5))
ground_group.add(ground(100,100,200,5))
ground_group.add(ground(700,830,800,60))
ground_group.add(ground(800,450,200,5))


while True:
    pygame.init()
    timer = pygame.time.get_ticks()
    pressed_keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_SPACE:
                player.gravitystate = True
            if event.key == K_r:
                player.rect.center = (140,50)
    if timer-stars_timer >= 100:
        for x in range(1,8):
            y = random.randint(0,880)
            stars_group.add(stars(y))
        stars_timer = timer
    screen.fill((0,0,0))
    player.update(pressed_keys)
    screen.blit(player.image,player.rect)
    stars_group.draw(screen)
    ground_group.draw(screen)
    stars_group.update()
    ground_group.update(pressed_keys)

    pygame.display.update()
    fps.tick(60)
