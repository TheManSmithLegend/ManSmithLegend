import pygame, sys, random, json
from pygame.locals import *
screen_width, screen_height = 1542, 880
screen = pygame.display.set_mode((screen_width, screen_height))
fps = pygame.time.Clock()
GROUND_LEVEL = 700
GRAVITY = 4
camera_right = False
camera_left = False

class stars(pygame.sprite.Sprite):
    def __init__(self,x):
        super(stars,self).__init__()
        self.image = pygame.Surface((1,1))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (screen_width,x))
    def update(self):
        self.rect.x -= 4
        if self.rect.x <= 0:
            self.kill()

class ground(pygame.sprite.Sprite):
    def __init__(self,gd_locx,gd_locy,gd_sizex,gd_sizey):
        super(ground,self).__init__()
        self.image = pygame.Surface((gd_sizex, gd_sizey))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(midleft = (gd_locx,gd_locy))
        self.movingr = False
        self.movingl = False
    def update(self, pressed_keys):
        global camera_right, camera_left
        #Camera View Mechanics
        if player.rect.center[0] >= ((screen_width+screen_width/2)/2):
            self.movingr = True
            self.movingl = False
        if player.rect.center[0]<= ((screen_width/2)/2):
            self.movingl = True
            self.movingr = False
        if self.movingr:
            self.rect.move_ip(-3,0)
            camera_right = True
            camera_left  = False
        if self.movingl:
            self.rect.move_ip(3,0)
            camera_left = True
            camera_right = False
        if abs(player.rect.center[0]-screen_width/2) <= 20:
            self.movingr = False
            self.movingl = False
            camera_left = False
            camera_right = False
            player.Rbasemove = 5
            player.Lbasemove = 5


class Player(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.Surface((50,50))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (screen_width/4,50))
        self.jump_vel = 30
        self.gravitystate = False
        self.moving = False
        self.Rbasemove = 5
        self.Lbasemove = 5
    def update(self, pressed_keys):
        global GRAVITY
        #jumping mechanics
        if self.gravitystate:
            self.rect.y -= self.jump_vel
            if self.jump_vel <= -30:
                self.jump_vel = -30
            else:
                self.jump_vel -= 3

        #Collisions
        player_gdcollisions = pygame.sprite.spritecollide(player, ground_group, dokill = False, collided = None)
        for x in player_gdcollisions:
            if abs(self.rect.bottom-x.rect.top) <= 30:
                self.rect.bottom = x.rect.top + 1
                self.jump_vel = 30
                self.gravitystate = False
                GRAVITY = 4
            elif abs(self.rect.top-x.rect.bottom) <= 30:
                self.rect.top = x.rect.bottom
                self.jump_vel = 30
                self.gravitystate = False
            elif abs(self.rect.left-x.rect.right) <= 20:
                self.rect.left = x.rect.right
            elif abs(self.rect.right-x.rect.left) <= 20:
                self.rect.right = x.rect.left

        #Controls and Camera View
        if pressed_keys[K_d]:
            self.rect.move_ip(self.Rbasemove,0)
        if pressed_keys[K_a]:
            self.rect.move_ip(-self.Lbasemove,0)
        #speed of character is changed based on the camera movement
        if camera_right:
            self.rect.move_ip(-3,0)
            self.Rbasemove = 6
            self.Lbasemove = 4
        if camera_left:
            self.rect.move_ip(3,0)
            self.Rbasemove = 4
            self.Lbasemove = 6

        #Gravity when in the state of freefall and not jumping
        if not player_gdcollisions and self.gravitystate == False:
            self.rect.y += GRAVITY
            if GRAVITY >= 28:
                GRAVITY = 28
            else:
                GRAVITY += 4

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
    yeet = pygame.key.get_focused()
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
