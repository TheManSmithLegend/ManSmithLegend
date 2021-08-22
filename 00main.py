import pygame, sys, random, json
from pygame.locals import *
screen_width, screen_height = 1542, 880
screen = pygame.display.set_mode((screen_width, screen_height))
fps = pygame.time.Clock()
jumpPower = 30
commonGravity = 4
camera_right = False
camera_left = False
levelSelected = "Level_1"

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
        global jumpPower
        self.image = pygame.Surface((50,70))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (screen_width/4,50))
        self.jump_vel = jumpPower
        self.facing = 1
        self.gravitystate = False
        self.gravity = commonGravity
        self.moving = False
        self.Rbasemove = 5
        self.Lbasemove = 5
    def update(self, pressed_keys):
        global jumpPower
        #jumping mechanics
        if self.gravitystate:
            self.rect.y -= self.jump_vel
            if self.jump_vel <= -jumpPower:
                self.jump_vel = -jumpPower
            else:
                self.jump_vel -= 2

        #Collisions
        player_gdcollisions = pygame.sprite.spritecollide(player, ground_group, dokill = False, collided = None)
        for x in player_gdcollisions:
            if abs(self.rect.bottom-x.rect.top) <= 30:
                self.rect.bottom = x.rect.top + 1
                self.jump_vel = jumpPower
                self.gravitystate = False
                self.gravity = 4
            elif abs(self.rect.top-x.rect.bottom) <= 30:
                self.rect.top = x.rect.bottom
                self.jump_vel = jumpPower
                self.gravitystate = False
            elif abs(self.rect.left-x.rect.right) <= 20:
                self.rect.left = x.rect.right
            elif abs(self.rect.right-x.rect.left) <= 20:
                self.rect.right = x.rect.left

        #Controls and Camera View
        if pressed_keys[K_d]:
            self.rect.move_ip(self.Rbasemove,0)
            self.facing = 1
        if pressed_keys[K_a]:
            self.rect.move_ip(-self.Lbasemove,0)
            self.facing = -1

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
            self.rect.y += self.gravity
            if self.gravity >= 28:
                self.gravity = 28
            else:
                self.gravity += 4

    def player_pos(self):
        return self.rect.center


class Projectile(pygame.sprite.Sprite):
    def __init__(self, posx, posy, facing):
        super(Projectile,self).__init__()
        self.image = pygame.Surface((8,8))
        self.image.fill((255,255,0))
        self.rect = self.image.get_rect(center = (posx, posy))
        self.vel = 10
        self.facing = facing
        self.damage = 10

    def update(self):
        self.rect.x += self.vel * self.facing
        if self.rect.x > screen_width or self.rect.x < 0:
            self.kill()
#to be added - SMART enemy class / enemy subclasses
class Enemy(pygame.sprite.Sprite):
    def __init__(self, posx, posy):
        super(Enemy,self).__init__()
        self.image = pygame.Surface((30,50))
        self.image.fill((255,50,50))
        self.rect = self.image.get_rect(center = (posx, posy))
        self.gravitystate = False
        self.jump_vel = jumpPower
        self.gravity = commonGravity

    def update(self):
        if self.gravitystate:
            self.rect.y -= self.jump_vel
            if self.jump_vel <= -jumpPower:
                self.jump_vel = -jumpPower
            else:
                self.jump_vel -= 2

        enemy_gdcollisions = pygame.sprite.groupcollide(enemies_group, ground_group, False, False, collided = None)
        for enemy in enemy_gdcollisions:
            print(enemy)
            print(enemy_gdcollisions[enemy])

class Minion(Enemy):
    def __init__(self, width, height, human_form):
        super().__init__(width, height)

def drawGameWindow():
    screen.fill((0,0,0))
    projectile_group.draw(screen)
    player.update(pressed_keys)
    screen.blit(player.image,player.rect)
    stars_group.draw(screen)
    ground_group.draw(screen)
    enemies_group.draw(screen)
    stars_group.update()
    ground_group.update(pressed_keys)
    projectile_group.update()
    enemies_group.update()
    pygame.display.update()

ground_group = pygame.sprite.Group()
stars_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()

with open("C:\\Users\\splin\\github\\ManSmithLegend\\data\\levels.json") as levels_file:
    levelData = json.load(levels_file)
    for item in levelData[levelSelected]['structures']:
        for args in item:
            ground_group.add(ground(*(tuple(item[args]))))
    for item in levelData[levelSelected]['enemies']:
        for args in item:
            enemies_group.add(Enemy(*(tuple(item[args]))))

player = Player()
stars_timer = 0
run = True
while run:
    pygame.init()
    timer = pygame.time.get_ticks()
    pressed_keys = pygame.key.get_pressed()
    yeet = pygame.key.get_focused()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                run = False
            if event.key == K_SPACE:
                player.gravitystate = True
            if event.key == K_r:
                player.rect.center = (140,50)
            if event.key == K_f:
                projectile_group.add(Projectile(player.rect.x+25, player.rect.y+30, player.facing))
    if timer-stars_timer >= 100:
        for x in range(1,8):
            y = random.randint(0,880)
            stars_group.add(stars(y))
        stars_timer = timer
    drawGameWindow()
    fps.tick(60)

pygame.quit()
sys.exit()
