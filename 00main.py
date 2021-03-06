import pygame, sys, random, json, os, math
from pygame.locals import *
from math import *
pygame.init()
cwd = os.getcwd()
screen_width, screen_height = 1542, 880
screen = pygame.display.set_mode((screen_width, screen_height),RESIZABLE)
fps = pygame.time.Clock()
sentrymode_time = pygame.USEREVENT + 0
quickground_time = pygame.USEREVENT + 1
slowground_time = pygame.USEREVENT + 2

pygame.time.set_timer(sentrymode_time, 3200)
pygame.time.set_timer(quickground_time, 4200)
pygame.time.set_timer(slowground_time, 7500)
jumpPower = 30
commonGravity = 2.5
camera_right = False
camera_left = False
camera_up = False
camera_down = False
levelSelected = "Level_1"

#BACKGROUND STAR VISUALS

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

#GROUND AND CAMERA MOVEMENT

class ground(pygame.sprite.Sprite):
    def __init__(self,gd_locx,gd_locy,gd_sizex,gd_sizey,motility,gd_movex,gd_movey,quickness):
        super(ground,self).__init__()
        self.image = pygame.Surface((gd_sizex, gd_sizey))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(midleft = (gd_locx,gd_locy))
        #Cam Vars
        self.movingr = False
        self.movingl = False
        self.movingu = False
        self.movingd = False
        #Move Vars
        self.motile = motility
        self.quickground = quickness
        self.movetoggle = True
        self.groundmovex = gd_movex
        self.groundmovey = gd_movey
    def update(self, pressed_keys):
        global camera_right, camera_left, camera_up, camera_down
        #Camera View Mechanics
        if player.rect.center[0] >= cam_rlimit:
            self.movingr = True
            self.movingl = False
        if player.rect.center[0]<= cam_llimit:
            self.movingl = True
            self.movingr = False
        if player.rect.center[1] >= cam_dlimit:
            self.movingd = True
            self.movingu = False
        if player.rect.center[1] <= cam_ulimit:
            self.movingu = True
            self.movingd = False
        if self.movingr:
            self.rect.move_ip(-3,0)
            camera_right = True
            camera_left  = False
        if self.movingl:
            self.rect.move_ip(3,0)
            camera_left = True
            camera_right = False
        if self.movingu and not player.gravitystate:
            self.rect.move_ip(0,4)
            camera_up = True
            camera_down = False
        if self.movingd:
            self.rect.move_ip(0,-4)
            camera_down = True
            camera_up = False
        if abs(player.rect.center[0]-current_hsw) <= ratio1:
            self.movingr = False
            self.movingl = False
            camera_left = False
            camera_right = False
            player.Rbasemove = 5
            player.Lbasemove = 5
        if player.rect.center[1]-current_hsh <= 10:
            self.movingd = False
            camera_down = False
        if player.rect.center[1]-current_hsh >= -10:
            self.movingu = False
            camera_up = False
        #Ground Movement Mechanics
        if self.motile:
            if self.movetoggle:
                self.rect.move_ip(self.groundmovex, self.groundmovey)
            elif not self.movetoggle:
                self.rect.move_ip(-self.groundmovex, -self.groundmovey)

#HEALTH - TO BE FIXED

class Health(pygame.sprite.Sprite):
    def __init__(self, posx, posy, health):
        super(Health,self).__init__()
        self.healthwidth = 45
        self.image = pygame.Surface((self.healthwidth, 12))
        self.image.fill((222,31,42))
        self.rect = self.image.get_rect(center = (posx, posy))
        self.maxhealth = health
        self.health = health

    def statuscheck(self, new_posx, new_posy, new_health):
        if self.health <= 0:
            self.kill()
        else:
            self.rect.center = (new_posx, new_posy-75)
            self.health = new_health
            self.fract = self.health/self.maxhealth
            self.image = pygame.transform.scale(self.image, (round(self.fract*self.healthwidth), 12))

#PLAYER

class Player(pygame.sprite.Sprite):
    def __init__(self):
        global jumpPower
        self.image = pygame.Surface((50,70))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (screen_width/4,50))
        #Jumping Vars
        self.gravitystate = False
        self.jump_vel = jumpPower
        #Falling Vars
        self.falltoggle = True
        self.falling = False
        self.gravity = commonGravity
        #Jetpack Vars
        self.jetstate = False
        self.startingthrust = 2
        self.optimalthrust = 6
        #Moving Vars
        self.moving = False
        self.Rbasemove = 5
        self.Lbasemove = 5
        self.facing = 1

    def update(self, pressed_keys):
        global jumpPower
        #Jumping mechanics
        if self.gravitystate and not self.falling and not self.jetstate:
            self.falltoggle = False
            self.jetstate = False
            self.rect.y -= self.jump_vel
            if self.jump_vel <= -jumpPower:
                self.jump_vel = -jumpPower
            else:
                self.jump_vel -= 2
        elif not self.jetstate:
            self.falltoggle = True
        #Collisions
        player_gdcollisions = pygame.sprite.spritecollide(player, ground_group, dokill = False, collided = None)
        for ground in player_gdcollisions:
            if abs(self.rect.bottom-ground.rect.top) <= 40:
                self.rect.bottom = ground.rect.top + 1
                self.jump_vel = jumpPower
                self.gravitystate = False
                self.gravity = 4
                if ground.motile == True:
                    if ground.movetoggle:
                        self.rect.move_ip(ground.groundmovex, ground.groundmovey)
                    else:
                        self.rect.move_ip(-ground.groundmovex, -ground.groundmovey)
            elif abs(self.rect.top-ground.rect.bottom) <= 40:
                self.rect.top = ground.rect.bottom
                self.jump_vel = jumpPower
                self.gravitystate = False
                if ground.motile == True:
                    self.rect.move_ip(0, 5)
            elif abs(self.rect.left-ground.rect.right) <= 30:
                self.rect.left = ground.rect.right
            elif abs(self.rect.right-ground.rect.left) <= 30:
                self.rect.right = ground.rect.left
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
            self.Rbasemove = 4
            self.Lbasemove = 4
        if camera_left:
            self.rect.move_ip(3,0)
            self.Rbasemove = 4
            self.Lbasemove = 4
        if camera_up:
            self.rect.move_ip(0,4)
        if camera_down:
            self.rect.move_ip(0,-4)
        #Gravity when in the state of freefall and not jumping
        if not player_gdcollisions and self.falltoggle:
            self.falling = True
            self.rect.y += self.gravity
            if self.gravity >= 28:
                self.gravity = 28
            else:
                self.gravity += 2
        else:
            self.falling = False
        #Jetpack when gravity and jumping is not in effect
        if pressed_keys[K_j]:
            self.jetstate = True
            self.falltoggle = False
            self.gravitystate = False
            self.rect.move_ip(0,-self.startingthrust)
            if self.startingthrust < self.optimalthrust:
                self.startingthrust += 0.2
        else:
            self.jetstate = False
            self.startingthrust = self.optimalthrust/3
    def player_pos(self):
        return self.rect.center

#WEAPONS

#PROJECTILES

class Projectile(pygame.sprite.Sprite):
    def __init__(self, posx, posy, facing):
        super(Projectile,self).__init__()
        self.image = pygame.Surface((8,8))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (posx, posy))
        self.facing = facing
        self.x_vel = 0
        self.y_vel = 0
        self.y_grav = 0
        self.damage = 0
        self.inair = True

    def update(self):
        if self.inair:
            self.rect.x += self.x_vel * self.facing
            self.rect.y -= self.y_vel
            self.y_vel -= self.y_grav

        if camera_right:
            self.rect.move_ip(-3,0)
        if camera_left:
            self.rect.move_ip(3,0)
        if camera_up:
            self.rect.move_ip(0,4)
        if camera_down:
            self.rect.move_ip(0,-4)

class ExplosivePepsi(Projectile):
    def __init__(self, posx, posy, facing):
        super().__init__(posx, posy, facing)
        self.sentrymode_imglist = []
        self.index = 0
        directory = os.path.join(cwd, "assets\ExplosivePepsi")
        for spritename in os.listdir(directory):
            i = os.path.join(directory, spritename)
            self.sentrymode_imglist.append(pygame.transform.scale(pygame.image.load(i), (16, 32)))
        self.image = self.sentrymode_imglist[0]
        self.rect = self.image.get_rect(center = (posx, posy))
        self.animtime = 0

        #PROJECTILE VARS
        self.x_vel = 6
        self.y_vel = 9
        self.y_grav = 0.4
        self.damage = 10

        #EXPLOSIVE VARS
        self.detonate = False

        #BOUNCE VARS
        self.bounceoff_floor = False
        self.bounceoff_roof = False
        self.bounceoff_right = False
        self.bounceoff_left = False
        self.friction = 0
        self.bouncefactor = 4
        self.x_velbounce = self.bouncefactor
        self.y_velbounce = self.bouncefactor
        self.y_gravbounce = 0.4


    def update(self):
        super().update()
        #STANDARD ANIMATION
        self.image = self.sentrymode_imglist[self.index]
        if self.animtime > 5:
            if self.index != len(self.sentrymode_imglist)-1:
                self.index += 1
            else:
                self.index = 0
            self.animtime = 0
        else:
            self.animtime += 1
        #COLLISIONS
        explosive_groundcollisions = pygame.sprite.spritecollide(self, ground_group, dokill = False, collided = None)
        for ground in explosive_groundcollisions:
            self.inair = False
            if abs(self.rect.bottom-ground.rect.top) <= 42:
                self.bounceoff_roof, self.bounceoff_right, self.bounceoff_left = False, False, False
                self.bounceoff_floor = True
                self.bouncefactor -= self.friction
                self.x_velbounce = self.bouncefactor
                self.y_velbounce = self.bouncefactor
            if abs(self.rect.top-ground.rect.bottom) <= 42:
                self.bounceoff_floor, self.bounceoff_right, self.bounceoff_left = False, False, False
                self.bounceoff_roof = True
            if abs(self.rect.left-ground.rect.right) <= 22:
                self.bounceoff_floor, self.bounceoff_right, self.bounceoff_roof = False, False, False
                self.bounceoff_left = True
            if abs(self.rect.right-ground.rect.left) <= 22:
                self.bounceoff_floor, self.bounceoff_left, self.bounceoff_roof = False, False, False
                self.bounceoff_right = True
        if self.bounceoff_floor and self.bouncefactor > 0:
            self.rect.x += self.x_velbounce * self.facing
            self.rect.y -= self.y_velbounce
            self.y_velbounce -= self.y_gravbounce
            self.friction += 0.025
        elif self.bounceoff_roof:
            self.rect.x += self.x_velbounce * self.facing
            self.rect.y += self.y_velbounce
            self.y_velbounce += self.y_gravbounce
        elif self.bounceoff_left:
            self.facing = 1
            self.rect.x += self.x_velbounce * self.facing
            self.rect.y += self.y_velbounce
            self.y_velbounce += self.y_gravbounce
        elif self.bounceoff_right:
            self.facing = -1
            self.rect.x += self.x_velbounce * self.facing
            self.rect.y += self.y_velbounce
            self.y_velbounce += self.y_gravbounce
        if self.detonate:
            print('boom')
            self.detonate = False

class CokeBlade(Projectile):
    def __init__(self, posx, posy, facing):
        super().__init__(posx, posy, facing)
        self.x_vel = 16
        self.y_vel = 0
        self.y_grav = 0.05
        self.damage = 2

    def update(self):
        super().update()
        blade_enemycollisions = pygame.sprite.spritecollide(self, enemies_group, dokill = False, collided = None)
        for enemy in blade_enemycollisions:
            enemy.health -= self.damage
            self.kill()

#MELEE
class Melee(pygame.sprite.Sprite):
    def __init__(self, posx, posy, facing):
        super(Melee,self).__init__()
        self.image = pygame.Surface((38,35))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (posx, posy))
        self.facing = facing
        self.attackspeed = 2
        self.damage = 2
        self.time = 0
        self.attacktimer = 12

    def update(self):
        if self.time >= self.attacktimer:
            self.kill()
        if self.facing == 1:
            self.rect.midleft = player.rect.midright
        if self.facing == -1:
            self.rect.midright = player.rect.midleft
        melee_enemycollisions = pygame.sprite.spritecollide(self, enemies_group, dokill = False, collided = None)
        for enemy in melee_enemycollisions:
            enemy.health -= self.damage
            self.kill()
        self.time += 1

#MINIONS:

#to be added - SMART enemy class / enemy subclasses
class StandardMinion(pygame.sprite.Sprite):
    def __init__(self, posx, posy, sentryspeed, attackspeed):
        super(StandardMinion,self).__init__()
        self.sentrymode_imglist = []
        self.index = 0
        directory = os.path.join(cwd, "assets\EnemySample1")
        for spritename in os.listdir(directory):
            i = os.path.join(directory, spritename)
            self.sentrymode_imglist.append(pygame.transform.scale(pygame.image.load(i), (60, 120)))
        self.image = self.sentrymode_imglist[0]
        self.rect = self.image.get_rect(center = (posx, posy))
        self.animtime = 0

        #Mechanics
        self.gravitystate = False
        self.falltoggle = True
        self.falling = False
        self.jump_vel = jumpPower
        self.gravity = commonGravity
        self.sentrymode = True
        self.sentrytoggle = True
        self.sentryspeed = sentryspeed
        self.attacktolerance = 280
        self.attackmode = False
        self.attacklocked = False
        self.attackspeed = attackspeed

        #Health
        self.health = 12
        self.healthbar = Health(self.rect.center[0], self.rect.center[1]-50,self.health)
        projectile_group.add(self.healthbar)

    def update(self):
        if self.health <= 0:
            self.kill()
        #STANDARD ANIMATION
        self.image = self.sentrymode_imglist[self.index]
        if self.animtime > 10:
            if self.index != len(self.sentrymode_imglist)-1:
                self.index += 1
            else:
                self.index = 0
            self.animtime = 0
        else:
            self.animtime += 1
        #ACTION MECHANICS
        if self.gravitystate and not self.falling:
            self.falltoggle = False
            self.rect.y -= self.jump_vel
            if self.jump_vel <= -jumpPower:
                self.jump_vel = -jumpPower
            else:
                self.jump_vel -= 2
        elif not self.attackmode:
            self.falltoggle = True
        enemy_enemycollisions = pygame.sprite.spritecollide(self, enemies_group, dokill = False, collided = None)
        for enemy in enemy_enemycollisions:
            if abs(self.rect.bottom-enemy.rect.top) <= 30:
                self.rect.bottom = enemy.rect.top + 1
                self.jump_vel = jumpPower
                self.gravitystate = False
                self.gravity = 4
            elif abs(self.rect.top-enemy.rect.bottom) <= 30:
                self.rect.top = enemy.rect.bottom
                self.jump_vel = jumpPower
                self.gravitystate = False
            elif abs(self.rect.left-enemy.rect.right) <= 10:
                self.rect.left = enemy.rect.right
            elif abs(self.rect.right-enemy.rect.left) <= 10:
                self.rect.right = enemy.rect.left

        enemy_gdcollisions = pygame.sprite.spritecollide(self, ground_group, dokill = False, collided = None)
        for ground in enemy_gdcollisions:
            if abs(self.rect.bottom-ground.rect.top) <= 30:
                self.rect.bottom = ground.rect.top + 1
                self.jump_vel = jumpPower
                self.gravitystate = False
                self.gravity = 4
            elif abs(self.rect.top-ground.rect.bottom) <= 30:
                self.rect.top = ground.rect.bottom
                self.jump_vel = jumpPower
                self.gravitystate = False
            elif abs(self.rect.left-ground.rect.right) <= 20:
                self.rect.left = ground.rect.right
            elif abs(self.rect.right-ground.rect.left) <= 20:
                self.rect.right = ground.rect.left
        if not enemy_gdcollisions and self.falltoggle and not self.attacklocked:
            self.rect.y += self.gravity
            if self.gravity >= 28:
                self.gravity = 28
            else:
                self.gravity += 4
        if camera_right:
            self.rect.move_ip(-3,0)
        if camera_left:
            self.rect.move_ip(3,0)
        if camera_up:
            self.rect.move_ip(0,4)
        if camera_down:
            self.rect.move_ip(0,-4)
        if self.sentrymode and not self.attacklocked:
            if self.sentrytoggle:
                self.rect.move_ip(self.sentryspeed,0)
            else:
                self.rect.move_ip(-self.sentryspeed,0)
        for enemy in enemies_group:
            enemy_coord = pygame.Vector2(enemy.rect.center)
            player_coord = pygame.Vector2(player.rect.center)
            if enemy_coord.distance_to(player_coord) < self.attacktolerance:
                enemy.attackmode = True
                enemy.sentrymode = False
            if enemy_coord.distance_to(player_coord) > self.attacktolerance:
                enemy.attackmode = False
                enemy.sentrymode = True
        self.healthbar.statuscheck(self.rect.center[0], self.rect.center[1], self.health)

class ExplosiveMinion(StandardMinion):
    def __init__(self, posx, posy, sentryspeed, attackspeed):
        super().__init__(posx, posy, sentryspeed, attackspeed)
        self.height = 0
        self.height_limit = 405
        self.flightspeed_y = 5
        self.target_acquired = None
        self.firespeed = 35

    def update(self):
        super().update()
        enemy_gdcollisions = pygame.sprite.spritecollide(self, ground_group, dokill = False, collided = None)
        enemy_playercollisions = pygame.sprite.spritecollide(player, enemies_group, dokill = False, collided = None)
        if self.attackmode and not self.sentrymode:
            self.attacklocked = True
        if self.attacklocked:
            if self.height < self.height_limit:
                self.height += self.flightspeed_y
                self.rect.y -= self.flightspeed_y
            else:
                if self.target_acquired is None:
                    self.target_acquired = findAngle(self.rect.x,self.rect.y,player.rect.x,player.rect.y)
                self.rect.x += math.cos(self.target_acquired) * self.firespeed
                self.rect.y += math.sin(self.target_acquired) * self.firespeed
                if enemy_gdcollisions or enemy_playercollisions:
                    self.health = 0


class RangedMinion(StandardMinion):
    def __init__(self, posx, posy, sentryspeed, attackspeed):
        super().__init__(posx, posy, sentryspeed, attackspeed)

    def update(self):
        super().update()
        if abs(self.rect.x-player.rect.x) < 100:
            #print("FIRE!")
            pass

class MeleeMinion(StandardMinion):
    def __init__(self, posx, posy, sentryspeed, attackspeed):
        super().__init__(posx, posy, sentryspeed, attackspeed)

    def update(self):
        super().update()
        if self.attackmode and not self.sentrymode:
            distance = player.rect.center[0] - self.rect.center[0]
            if distance > 0:
                self.rect.move_ip(self.attackspeed,0)
            if distance < 0:
                self.rect.move_ip(-self.attackspeed,0)

#ANGLE FINDER
def findAngle(x,y,x2,y2):
    deltaX = x2 - x
    deltaY = y2 - y
    return math.atan2(deltaY,deltaX)

#DRAWING FUNCTION
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
    melee_group.update()
    enemies_group.update()
    pygame.display.update()

#TESTING CAMERA SETUP
def cameraConfig():
    global cam_rlimit, cam_llimit, cam_dlimit, cam_ulimit, current_hsw, current_hsh, ratio1
    current_sw, current_sh = screen.get_size()
    current_hsw, current_hsh = current_sw/2, current_sh/2
    cam_rlimit = current_hsw+(current_hsw/2-current_hsw/4)
    cam_llimit = current_hsw-(current_hsw/2-current_hsw/4)
    cam_dlimit = current_hsh+(current_sh*0.170)
    cam_ulimit = current_hsh-(current_sh*0.091)
    ratio1 = current_sw*0.013
    ratio2 = current_sh*0.170
    ratio3 = current_sh*0.091
    cam_umid = int(current_hsh - ratio3)
    cam_dmid = current_hsh + ratio2

#PYGAME SPRITES
ground_group = pygame.sprite.Group()
stars_group = pygame.sprite.Group()
health_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
melee_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()


#JSON ACCESS
accessLevels = os.path.join(cwd, "data\levels.json")
with open(accessLevels) as levels_file:
    levelData = json.load(levels_file)
#SPAWN MAP
    for item in levelData[levelSelected]['structures']:
        ground_group.add(ground(*(tuple(levelData[levelSelected]['structures'][item]))))
#SPAWN ENEMIES
    for spawn in levelData[levelSelected]['enemies']["ExplosiveMinion"]:
        enemies_group.add(ExplosiveMinion(*(tuple(levelData[levelSelected]['enemies']["ExplosiveMinion"][spawn]))))
    for spawn in levelData[levelSelected]['enemies']["RangedMinion"]:
        enemies_group.add(RangedMinion(*(tuple(levelData[levelSelected]['enemies']["RangedMinion"][spawn]))))
    for spawn in levelData[levelSelected]['enemies']["MeleeMinion"]:
        enemies_group.add(MeleeMinion(*(tuple(levelData[levelSelected]['enemies']["MeleeMinion"][spawn]))))


player = Player()
stars_timer = 0
run = True
while run:
    timer = pygame.time.get_ticks()
    pressed_keys = pygame.key.get_pressed()
    cameraConfig()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                run = False
            if event.key == K_SPACE and not player.jetstate:
                player.gravitystate = True
            if event.key == K_r:
                player.rect.kill()
            if event.key == K_b:
                projectile_group.add(CokeBlade(player.rect.x+25, player.rect.y+30, player.facing))
            if event.key == K_g:
                projectile_group.add(ExplosivePepsi(player.rect.x+25, player.rect.y+30, player.facing))
            if event.key == K_v:
                melee_group.add(Melee(player.rect.center[0], player.rect.center[1], player.facing))
            if event.key == K_x:
                for sprite in projectile_group:
                    if hasattr(sprite, 'detonate'):
                        sprite.detonate = True
            if event.key == K_j:
                player.gravitystate = False
        if event.type == sentrymode_time:
            for enemy in enemies_group:
                enemy.sentrytoggle = not enemy.sentrytoggle
        if event.type == quickground_time:
            for ground in ground_group:
                if ground.quickground:
                    ground.movetoggle = not ground.movetoggle
        if event.type == slowground_time:
            for ground in ground_group:
                if not ground.quickground:
                    ground.movetoggle = not ground.movetoggle
    if timer-stars_timer >= 100:
        for x in range(1,8):
            y = random.randint(0,880)
            stars_group.add(stars(y))
        stars_timer = timer
    drawGameWindow()
    fps.tick(60)

pygame.quit()
sys.exit()
