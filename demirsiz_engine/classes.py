import pygame
from . import spritegroups
from . import functions

SCALE_FACTOR=3

class Border(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,width,height,color,isWallJumpable=True):
        pygame.sprite.Sprite.__init__(self)

        self.pos_x=pos_x
        self.pos_y=pos_y
        
        self.height=height
        self.width=width
        self.color=color
        
        self.isWallJumpable=isWallJumpable
        
        self.image=pygame.Surface((width,height))
        self.image.fill(color)

        self.rect=self.image.get_rect()
        self.rect.topleft=(self.pos_x,self.pos_y)

    @staticmethod
    def calculateBorders(screen,borderThickness):
        topBorder=Border(0,0,screen.get_width(),borderThickness,(0,0,0))
        bottomBorder=Border(0,screen.get_height()-borderThickness,screen.get_width(),borderThickness,(0,0,0))
        leftBorder=Border(0,0,borderThickness,screen.get_height(),(0,0,0))
        rightBorder=Border(screen.get_width()-borderThickness,0,borderThickness,screen.get_height(),(0,0,0))

        return (topBorder,bottomBorder,leftBorder,rightBorder)

class Mob(pygame.sprite.Sprite):
    def __init__(
        self,
        name,
        hp,
        dmg,
        spd,
        pos_x,
        pos_y,
        type=1,
        shape=1,
        radius=25,
        width=10,
        length=25,
        color=(0,0,0),
        isAlive=True,
        jumpStr=1,
        g=2000,
        canFall=True,
        canWallJump=False,
        dyingSprite=None,
        ):

        pygame.sprite.Sprite.__init__(self)
            
        self.hp=hp 
        self.dmg=dmg
        self.spd=spd
        self.type=type
        self.name=name
        self.pos_x=pos_x
        self.pos_y=pos_y
        self.radius=radius
        self.width=width
        self.length=length
        self.color=color
        self.baseSpd=spd
        self.jumpStr=jumpStr
        self.shape=shape
        self.dyingSprite=dyingSprite

        self.deathDuration=1
        self.deathTimer=self.deathDuration
        self.isDying=False
        self.isAlive=True
        self.isJumping=False
        self.isFalling=False
        self.isSprinting=False
        self.verticalVelocity=0
        self.g=g
        self.isGrounded=False
        self.canFall=canFall
        self.canWallJump=canWallJump
        self.facing="default"
           
    def initialDraw(self):
        if(self.shape==1):
            self.image=pygame.Surface((2*self.radius,2*self.radius),pygame.SRCALPHA)
            self.image.fill((0,0,0,0))
            pygame.draw.circle(self.image,self.color,(self.radius,self.radius),self.radius)
        elif(self.shape==2):
            if(self.image==None):
                self.image=pygame.Surface((self.width,self.length),pygame.SRCALPHA)
                self.image.fill((0,0,255,100))
        self.rect=self.image.get_rect()
        self.rect.center=(self.pos_x,self.pos_y)
    
    def __str__(self):
        return self.name
        
    def useAttack(self,other):
        if((self.type>0 and self.isAlive==True) and other.isAlive):
            other.hp=other.hp-self.dmg
            if(other.hp<=0):              
                other.kill()
                print(f"{self} attacked {other}, dealing a damage of {self.dmg}, killing {other}.")
            else:
                print(f"{self} attacked {other}, dealing a damage of {self.dmg}. {other}'s new hp is {other.hp}")

    def walk(self,direction,dt):
        
        blockedDirections=self.checkCollision(spritegroups.solidObjects)[0]
               
        if(direction=="up"):
            if (blockedDirections.count("up")==0):
                self.pos_y -= self.spd * dt
                    
        if(direction=="down"):
            if(blockedDirections.count("down")==0):
                self.pos_y += self.spd * dt
                       
        if(direction=="left"):
            self.facing="left"
            if(blockedDirections.count("left")==0):
                self.pos_x -= self.spd * dt
        
        if(direction=="right"):
            self.facing="right"
            if(blockedDirections.count("right")==0):
                self.pos_x += self.spd * dt

        self.rect.center=(self.pos_x,self.pos_y)
        blockedDirections.clear()

    def jump(self):
        #print("jump")
        blockedDirections=self.checkCollision(spritegroups.solidObjects)[0]
        lastHorizontalCollider=self.checkCollision(spritegroups.solidObjects)[2]
        if("down" in blockedDirections):  
            self.verticalVelocity= -self.jumpStr
            self.isJumping=True
            self.isFalling=False
            
        if(self.canWallJump==True):
            #print("Wall jump checked. Blocked directions:", blockedDirections)
            if(getattr(lastHorizontalCollider,"isWallJumpable",False)):
                if("left" in blockedDirections or "right" in blockedDirections):
                    self.verticalVelocity= -self.jumpStr
                    self.isJumping=True
                    self.isFalling=False
            
    def sprint(self,toggle=True):
        if(self.isGrounded):
            if(toggle==True):
                if(self.isSprinting==False):
                    self.spd=2*self.spd
                    self.isSprinting=True
            else:
                self.spd=self.baseSpd
                self.isSprinting=False
            
    def checkCollision(self,spriteGroup):
        listOfCollidingSolidObjects=pygame.sprite.spritecollide(self,spriteGroup,False)
        blockedDirections=[]
        lastVerticalCollider=None
        lastHorizontalCollider=None
        
        for object in listOfCollidingSolidObjects:
            collisionsHorizontalDirection , collisionsVerticalDirection, lastVerticalCollider, lastHorizontalCollider = functions.rectCollisionDirection(self,object)
            blockedDirections.append(collisionsHorizontalDirection)
            blockedDirections.append(collisionsVerticalDirection)
            
        if("down"in blockedDirections):
            self.isGrounded=True
            
        return blockedDirections, lastVerticalCollider, lastHorizontalCollider

    def update(self,dt):
        if(self.isDying==True):
            #print(f"[{self.name}] Updating while dying... image id is: {id(self.image)}")
            if(self.deathTimer>0):
                self.deathTimer-=dt
            else:
                self.deathTimer=0
                self.kill()
                
        if(self.isJumping==True):
            self.verticalVelocity+=dt*self.g
            self.pos_y+=self.verticalVelocity*dt
            self.rect.center=(self.pos_x,self.pos_y)
            blockedDirections=self.checkCollision(spritegroups.solidObjects)[0]
            if(self.verticalVelocity<0 and "up" in blockedDirections):
                self.pos_y-=self.verticalVelocity*dt
                self.rect.center=(self.pos_x,self.pos_y)
                self.verticalVelocity=0
                self.isJumping=False
                self.isFalling=True
            if(self.verticalVelocity>0):
                self.isJumping=False
                self.isFalling=True
                
        blockedDirections=self.checkCollision(spritegroups.solidObjects)[0]
        if("down" not in blockedDirections and self.canFall==True):
            if(self.isJumping==False): 
                self.isFalling=True
            self.isGrounded=False
            
        if(self.isFalling==True):
            self.verticalVelocity+=dt*self.g
            blockedDirections=self.checkCollision(spritegroups.solidObjects)[0]
            #print(blockedDirections)
            if(self.verticalVelocity>0 and "down" in blockedDirections):
                if(self==self.checkCollision(spritegroups.solidObjects)[1]):
                    self.rect.bottom=self.checkCollision(spritegroups.solidObjects)[1].rect.bottom
                else:
                    self.rect.bottom=self.checkCollision(spritegroups.solidObjects)[1].rect.top+1
                    self.pos_y=self.rect.centery
                    self.verticalVelocity=0
                    self.isFalling=False
                self.isGrounded=True
            else:
                self.pos_y+=self.verticalVelocity*dt
                self.rect.center=(self.pos_x,self.pos_y)
            
    def kill(self):
        #print(f"[{self.name}] KILL CALLED! Old image id: {id(self.image)}")
        if(self.isDying==False):
            self.isDying=True
            self.isAlive=False
        self.hp=0
        self.image.fill((0,0,0,0))
        if(self.shape==1):
            pygame.draw.circle(self.image,(255,0,0,100),(self.radius,self.radius),self.radius)
        elif(self.shape==2):
            if(self.dyingSprite==None):
                self.dyingSprite=pygame.Surface(self.rect.size,pygame.SRCALPHA)
                self.dyingSprite.fill((255,0,0,100))
            self.image=self.dyingSprite
        #print(f"[{self.name}] New red image id: {id(self.image)}")
        
        if(self.deathTimer==0):
            pygame.sprite.Sprite.kill(self)
            self.isDying=False

class Wall(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,width,height,color="yellow",isWallJumpable=False,texture=None):
        pygame.sprite.Sprite.__init__(self)
        
        self.pos_x=pos_x
        self.pos_y=pos_y
        
        self.isWallJumpable=isWallJumpable
        
        self.image=pygame.Surface((width,height),pygame.SRCALPHA)
        self.image.fill(color)
        
        self.rect=self.image.get_rect()
        self.rect.topleft=(self.pos_x,self.pos_y)
 
class Weapon(pygame.sprite.Sprite):
    def __init__(self,name, dmg, cooldown, owner, range=25, type=1, attackDuration=0.3, texture=None):
        pygame.sprite.Sprite.__init__(self)  
        
        self.name=name
        self.dmg=dmg
        self.range=range
        self.cooldown=cooldown
        self.owner=owner
        self.type=type     
        self.attackDuration=attackDuration
        self.texture=texture
        
        self.isReady=True
        self.isAttacking=False
        self.cooldownTimer=self.cooldown
        self.attackTimer=self.attackDuration
        
        if(self.texture==None):
            self.image=pygame.Surface((range,10),pygame.SRCALPHA)
            self.image.fill((0,0,100,0))
            self.texture=self.image
        else:
            self.image=self.texture
        self.rect=self.image.get_rect()
        self.range=self.rect.width-5
        
    def __str__(self):
        return self.name
        
    def update(self,dt):
        if(self.isReady==False):
            self.cooldownTimer-=dt
            if(self.cooldownTimer<=0):
                self.isReady=True
                self.cooldownTimer=self.cooldown
                
        if(self.isAttacking==True):
            self.attackTimer-=dt
            if(self.owner.facing=="right"):
                self.image=self.texture
                self.rect.topleft=(self.owner.rect.right-5,self.owner.pos_y+5)
            elif(self.owner.facing=="left"): 
                self.image=pygame.transform.flip(self.texture,True,False)
                self.rect.topright=(self.owner.rect.left+5,self.owner.pos_y+5)
            self.image.set_alpha(255)
            if(self.attackTimer<=0):
                self.image.set_alpha(0)
                self.isAttacking=False
                self.attackTimer=self.attackDuration
            
            
    def useAttack(self,owner,other):
            if(self.isReady==True):
                horizontalDistance, verticalDistance, relativeDirection=functions.spriteDistance(owner,other)
                self.isReady=False
                self.isAttacking=True
                self.cooldownTimer=self.cooldown
                #print("usedattack")
                #print(relativeDirection)
                if(relativeDirection==owner.facing):
                    if(horizontalDistance<=self.range and verticalDistance<=0):
                        if(other.isAlive==True):
                            other.hp=other.hp-self.dmg
                            #print("damaged")
                            if(other.hp<=0):
                                other.kill()
                                print(f"{owner} attacked {other} using {self}, dealing a damage of {self.dmg}, killing {other}.")
                            else:
                                print(f"{owner} attacked {other} using {self}, dealing a damage of {self.dmg}. {other}'s new hp is {other.hp}")
            
class SpriteSheet(pygame.sprite.Sprite):
    def __init__(self,filePath):
        self.filePath=filePath
        self.spriteSheet=pygame.image.load(filePath).convert_alpha()
    def getSprite(self,pos_x,pos_y,width,height):
        rawSprite=pygame.Surface((width,height),pygame.SRCALPHA)
        rawSprite.blit(self.spriteSheet,(0,0),(pos_x,pos_y,width,height))
        sprite=pygame.transform.scale(rawSprite,(width*SCALE_FACTOR,height*SCALE_FACTOR))
        return sprite
        