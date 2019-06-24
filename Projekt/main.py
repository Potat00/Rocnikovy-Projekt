import pygame
from pygame.locals import *

#Init

getTicksLastFrame = 0;
deltaTime = 0;
clock = pygame.time.Clock()
gameStart = False

class LevelLoader():
    def __init__(self):
        self.sprites = pygame.sprite.Group();
        self.enemies = pygame.sprite.Group();
    def Load(self, file):
        with open(file,"r")as file:
            file_content = file.read().strip().split('\n');
            level_dymension = file_content[0].split()

            for i in range(0,int(level_dymension[0])):
                line = file_content[i+1].split()
                for j in range(0,int(level_dymension[1])):
                    position = Position(j*100, i*100)
                    if line[j] != '.':
                        if line[j] == '4':
                            position = Position(j*100, i*100+10)
                            self.sprites.add( SpecialBlock(line[j] + '.png', position,(100,100), False, True))
                        elif line[j] == 'x':
                            position = Position(j*100, i*100)
                            self.enemies.add(Enemy(position))
                        elif line[j] == 'y':
                            position = Position(j*100, i*100)
                            self.enemies.add(Enemy(position, True))
                        elif line[j] == '6':
                            self.sprites.add( SpecialBlock(line[j] + '.png', position,(100,100),False, False, True))
                        elif line[j][0] == 'd':
                            self.sprites.add( SpecialBlock('door.png', position,(100,100),False, False, True, line[j][1]))
                        elif line[j] == '7':
                            self.sprites.add( SpecialBlock(line[j] + '.png', position,(100,100),False, False, True))
                        else:
                            self.sprites.add( SpecialBlock(line[j] + '.png', position,(100,100),True))
    def Get_Level(self):
        return self.sprites

    def Get_enemies(self):
        return self.enemies.copy()

class Position():
    def __init__(self,x = 0,y = 0):
        self.x = x
        self.y = y

class SpriteAnimation():
    def __init__(self,default_image, interval = 0.1):
        self.image = default_image
        self.interval = interval
        self.intervalTime = 0
        self.sequences = dict()
        self.currentSequence = None
        self.sequenceIterator = 0;
        self.fliped = False
    def Play(self, sequence, flip = None):
        self.currentSequence = sequence
        if flip != None:
            self.fliped = flip
    def Iterate(self):
        if self.sequenceIterator < len(self.sequences[self.currentSequence]):
            self.image = self.sequences[self.currentSequence][self.sequenceIterator]
            self.sequenceIterator += 1
        else:
            self.sequenceIterator = 0
    def Update(self):
        if self.currentSequence != None:
            if self.intervalTime < self.interval:
                self.intervalTime += deltaTime
            else:
                self.Iterate()
                self.intervalTime = 0


    def Add(self, name, imageName):
        image = pygame.image.load(imageName).convert()
        image.set_colorkey((255,255,255))
        self.sequences[name].append(image)

    def CreateSequence(self, name):
        self.sequences[name] = list()

    def GetImage(self):
        if self.fliped:
            return pygame.transform.flip(self.image,True,False)
        else:
            return self.image

class Block(pygame.sprite.Sprite):

    def __init__(self,img = None, position = Position(0,0), dymensions = (100,100)):
        self.isGrounded = False;
        self._position = position

        pygame.sprite.Sprite.__init__(self)
        if img:
            self.image = pygame.image.load(img).convert()
        else:
            self.image = pygame.Surface(dymensions)
            self.image.fill((255,0,255));

        self.image.set_colorkey((255,255,255))

        self.rect = self.image.get_rect()
        self.rect.midbottom = (self._position.x, self._position.y)
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self,value):
        self._position = value
        self.rect.midbottom = (self._position.x, self._position.y)

class SpecialBlock(Block):
    def __init__(self,img = None, position = Position(0,0),dymensions = (100,100), isSolid = True, isDangerous = False, health = False, door = None):
        super().__init__(img, position, dymensions)
        self.isSolid = isSolid;
        self.isDangerous = isDangerous
        self.health = health
        self.door = door


class Bulet(Block):
    def __init__(self, Position = Position(0,0), direction = False, coliders = []):
        super().__init__('bullet.png', Position, (10,10))
        if direction:
            self.image = pygame.transform.flip(self.image,True, False)
        self.direction = direction
        self.collider_list = coliders
        self.hit = False;

    def Update(self, enemy):
        if self.direction:
            self._position = Position(self._position.x + deltaTime*1000*-1, self._position.y)
        else:
            self._position = Position(self._position.x + deltaTime*1000, self._position.y)

        if self.direction:
            self.rect.center = (self._position.x-15, self._position.y-44)
        else:
            self.rect.center = (self._position.x+35, self._position.y-44)
        hit = pygame.sprite.spritecollide(self,self.collider_list,False)
        if hit:
            self.hit = True
        hit = pygame.sprite.spritecollide(self,enemy,False)
        if hit:
            hit[0].health -= 10;
            self.hit = True

class Enemy(Block):
    def __init__(self, position = Position(0,0), canJump = False):
        super().__init__('Enemy/iddle.png', position)
        self.rect = self.image.get_rect()
        #self.rect.move_ip(20,50)

        self.health = 100

        self.direction = False
        self.canJump = canJump

        self.animator = SpriteAnimation(self.image)
        self.animator.CreateSequence("walk")
        self.animator.CreateSequence("iddle")
        self.animator.Add("walk","Enemy/walk1.png")
        self.animator.Add("walk","Enemy/walk2.png")
        self.animator.Add("iddle","Enemy/iddle.png")
        self.animator.Play("walk")


        self.vel_y = 0
        self.rightObstacle = False
        self.leftObstacle = False
        self.animationInterval = 0

    def Update(self,coliders, bulets):
        self.coliders = pygame.sprite.Group()
        self.coliders.add(coliders)
        self.coliders.add(bulets)
        #print(self.coliders)
        self.position.y += self.vel_y * deltaTime*300
        self.vel_y += 5 * deltaTime

        self.rect.midbottom = (self._position.x, self._position.y)
        hitss = pygame.sprite.spritecollide(self,coliders,False)
        if hitss:
            left = False
            right = False
            for hits in hitss:
                if self.rect.midright[0] > hits.rect.midleft[0] and self.rect.midleft[0] < hits.rect.midright[0] and self.rect.centery < hits.rect.midtop[1]:
                    self._position = Position(self._position.x,hits.rect.top)
                    if self.vel_y > 0:
                        self.isGrounded = True;
                        self.vel_y = 0

                else:
                    self.isGrounded = False;
                    self.vel_y += deltaTime
                if self.rect.centerx > hits.rect.midleft[0] and self.rect.centerx < hits.rect.midright[0] and self.rect.centery > hits.rect.midtop[1]:
                    self.vel_y = 0.01
                if self.rect.centerx < hits.rect.midleft[0] and self.rect.centery > hits.rect.midtop[1]:
                    self.rightObstacle = True
                    right = True
                else:
                    if not right:
                        self.rightObstacle = False
                if self.rect.centerx > hits.rect.midright[0] and self.rect.centery > hits.rect.midtop[1]:
                    self.leftObstacle = True
                    left = True
                else:
                    if not left:
                        self.leftObstacle = False

                #if hits.isDangerous == True:
                    #self._position = Position(0,0)
                #print(type(hits))
                #if isinstance(hits, Bulet):
                #    self.health -= 10


        else:
            self.rightObstacle = False
            self.leftObstacle = False
            self.isGrounded = False;

        self.InputUpdate()
        self.animator.Update()
        self.image = self.animator.GetImage()

        self.rect.midbottom = (self._position.x, self._position.y)

    def InputUpdate(self):
        self.animator.Play("iddle")

        if self.leftObstacle or self.rightObstacle:
            self.direction = not self.direction


        if self.direction and not self.rightObstacle:
            self._position = Position(self._position.x + (200 * deltaTime), self._position.y)
            self.animator.Play("walk", False)
        if not self.direction and not self.leftObstacle:
            self._position = Position(self._position.x - (200 * deltaTime), self._position.y)
            self.animator.Play("walk",True)


        if self.isGrounded and self.canJump:
            self.vel_y = -2

class Player(Block):
    def __init__(self):
        super().__init__('Player/iddle.png', Position(200,100))
        self.rect = self.image.get_rect().inflate(-20,0)
        self.rect.move_ip(20,50)

        self.health = 100

        self.animator = SpriteAnimation(self.image)
        self.animator.CreateSequence("walk")
        self.animator.CreateSequence("iddle")
        self.animator.Add("walk","Player/walk1.png")
        self.animator.Add("walk","Player/walk2.png")
        self.animator.Add("iddle","Player/iddle.png")
        self.animator.Play("walk")


        self.vel_y = 0
        self.rightObstacle = False
        self.leftObstacle = False
        self.animationInterval = 0

        self.bullets = []

    def Update(self,coliders, enemies):
        self.coliders = coliders
        self.position.y += self.vel_y * deltaTime*300
        self.vel_y += 5 * deltaTime

        self.rect.midbottom = (self._position.x, self._position.y)
        hitss = pygame.sprite.spritecollide(self, coliders, False)
        if hitss:
            left = False
            right = False
            for hits in hitss:
                #colision
                if hits.isSolid:
                    if self.rect.midright[0] > hits.rect.midleft[0] and self.rect.midleft[0] < hits.rect.midright[0] and self.rect.centery < hits.rect.midtop[1]:
                        self._position = Position(self._position.x,hits.rect.top)
                        if self.vel_y > 0:
                            self.isGrounded = True;
                            self.vel_y = 0
                    else:
                        self.isGrounded = False;
                        self.vel_y += deltaTime
                    if self.rect.centerx > hits.rect.midleft[0] and self.rect.centerx < hits.rect.midright[0] and self.rect.centery > hits.rect.midtop[1]:
                        self.vel_y = 0.01
                    if self.rect.centerx < hits.rect.midleft[0] and self.rect.centery > hits.rect.midtop[1]:
                        self.rightObstacle = True
                        right = True
                    else:
                        if not right:
                            self.rightObstacle = False
                    if self.rect.centerx > hits.rect.midright[0] and self.rect.centery > hits.rect.midtop[1]:
                        self.leftObstacle = True
                        left = True
                    else:
                        if not left:
                            self.leftObstacle = False

                #ine
                if hits.isDangerous == True :
                    self.health -= 10
                if self.health <= 0:
                    self.health = 100
                    self.position = Position(200,100)
                    LoadLevel(1)

                if hits.health == True :
                    self.health += 30*deltaTime
                    if self.health > 100:
                        self.health = 100

                if hits.door:
                    LoadLevel(hits.door)

        else:
            self.rightObstacle = False
            self.leftObstacle = False
            self.isGrounded = False;

        hits = pygame.sprite.spritecollide(self, enemies, False)
        if hits:
            for hit in hits:
                self.health -= 50*deltaTime

        if self.position.y > 10000:
            LoadLevel(1)
            
        self.InputUpdate()
        self.animator.Update()
        self.image = self.animator.GetImage()


        self.rect.midbottom = (self._position.x, self._position.y)

    def InputUpdate(self):
        self.animator.Play("iddle")

        if pygame.key.get_pressed()[K_d] and not self.rightObstacle:
            self._position = Position(self._position.x + (300 * deltaTime), self._position.y)
            self.animator.Play("walk", False)

        if pygame.key.get_pressed()[K_a] and not self.leftObstacle:
            self._position = Position(self._position.x - (300 * deltaTime), self._position.y)
            self.animator.Play("walk",True)

        if pygame.key.get_pressed()[K_w]:
            if self.isGrounded:
                self.vel_y = -2
                #self._position = Position(self._position.x, self._position.y - (100 * deltaTime))

def Camera(targetPosition, screen, position = None):
    if position:
        pos = Position(-targetPosition.x + (screen.get_size()[0]/2), -targetPosition.y + (screen.get_size()[1]/2))
        return Position(pos.x + position.x, pos.y + position.y)
    else:
        return Position(-targetPosition.x + (screen.get_size()[0]/2), -targetPosition.y + (screen.get_size()[1]/2))

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self, surface, camera):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            rect = spr.rect.copy()
            rect.x += camera.x
            rect.y += camera.y
            self.spritedict[spr] = surface_blit(spr.image, rect)
        self.lostsprites = []

def deltaTimeUpdate():
    #global getTicksLastFrame
    global deltaTime
    global clock
    #_time = pygame.time.get_ticks()
    #deltaTime = (_time - getTicksLastFrame) / 1000.000
    #getTicksLastFrame = _time
    deltaTime = clock.get_time() / 1000.000

def DrawHealthBar(position, health, surface, width):
    x = (health/100)
    g = 2.0 * x
    r = 2.0 * (1 - x)

    if r > 1.0:
        r = 1
    if g > 1.0:
        g = 1
    if r < 0:
        r = 0
    if g < 0:
        g = 0
    color = (r*255, g*255, 0)
    pygame.draw.rect(surface, color, (position.x, position.y, width * (health/100) ,5))

def LoadLevel(LevelId):
    global gameStart
    global deltaTime
    global block_list
    global collider_list
    global bulets
    global bulets_coliders
    global playerObj
    global level
    global enemies

    gameStart = False
    deltaTime = 0
    block_list = CameraGroup()
    collider_list = pygame.sprite.Group()
    bulets = CameraGroup()
    bulets_coliders = pygame.sprite.Group()

    playerObj = Player();
    block_list.add(playerObj);

    #level LevelLoader
    level = LevelLoader()
    level.Load("Level"+ str(LevelId) +".txt")
    block_list.add(level.Get_Level())
    collider_list.add(level.Get_Level())

    enemies = CameraGroup()
    enemies.add(level.Get_enemies())

def Game():
    global gameStart
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Game')
    pygame.font.init()
    font = pygame.font.SysFont('Comic Sans MS', 30)
    textsurface = font.render('Press Any Key To Start...', False, (0, 0, 0))
    background = pygame.image.load("background.jpg").convert()

    background = pygame.transform.scale(background, screen.get_size())



    LoadLevel(1)


    t_second = 0;

    while 1:
        screen.blit(background, (0,0))
        if gameStart:
            deltaTimeUpdate()
            pass
        else:
            screen.blit(textsurface,(250,0))

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                gameStart = True


        playerObj.Update(collider_list, enemies)


        t_second += deltaTime
        if pygame.key.get_pressed()[K_SPACE]:
            if t_second > 0.1:
                bulet = Bulet(playerObj.position, playerObj.animator.fliped, collider_list)
                bulets.add(bulet)
                bulets_coliders.add(bulet)
                t_second = 0



        for bulet in bulets:
            if bulet.hit:
                #bulets.remove(bulet)
                bulet.kill()
            else:
                bulet.Update(enemies)



        DrawHealthBar(Camera(playerObj.position, screen, Position(playerObj.rect.topleft[0], playerObj.rect.topleft[1]-20)), playerObj.health, screen, playerObj.rect.width*1.4)
        for enemy in enemies:
            if enemy.position.y > 50000:
                #enemies.remove(enemy)
                enemy.kill()
            if enemy.health <= 0:
                #enemies.remove(enemy)
                enemy.kill()
            else:
                enemy.Update(collider_list, bulets_coliders)
                DrawHealthBar(Camera(playerObj.position, screen, Position(enemy.rect.topleft[0], enemy.rect.topleft[1] - 10)), enemy.health, screen,enemy.rect.width)


        bulets.draw(screen, Camera(playerObj.position,screen))
        enemies.draw(screen, Camera(playerObj.position,screen))
        block_list.draw(screen, Camera(playerObj.position,screen))

        pygame.display.flip()
        clock.tick()



if __name__ == '__main__': Game()
