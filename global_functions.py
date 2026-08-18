import math
import pygame
import spriteGroups
import myClasses

def circleCollision(circle1:pygame.sprite.Sprite,circle2:pygame.sprite.Sprite):
    dx=(circle1.posx-circle2.posx)
    dy=(circle1.posy-circle2.posy)
    distance=math.sqrt((dx*dx)+(dy*dy))
    if(distance<(circle1.radius+circle2.radius)):
        if(circle1.hp>0 and circle2.hp>0):
            return(True)
        else:
            return(False)
    else:
        return(False)

def rectCollisionDirection(self,other:pygame.sprite.Sprite):
    collisionsVerticalDirection="default"
    collisionsHorizontalDirection="default"
    
    lastVerticalObject=self
    lastHorizontalObject=self
    
    leftOverlap = self.rect.right - other.rect.left
    rightOverlap= other.rect.right - self.rect.left
    topOverlap= self.rect.bottom - other.rect.top
    bottomOverlap=other.rect.bottom - self.rect.top
            
    minOverlapX=min(leftOverlap,rightOverlap)
    minOverlapY=min(topOverlap,bottomOverlap)
            
    if minOverlapY<minOverlapX:
        #vertical collision
        lastVerticalObject=other
        if(self.posy>other.posy):
            collisionsVerticalDirection="up"
        elif(self.posy<other.posy):
            collisionsVerticalDirection="down"
            
    elif(minOverlapX<minOverlapY):
        #horizontal collision
        lastHorizontalObject=other
        if(self.posx>other.posx):
            collisionsHorizontalDirection="left"
        elif(self.posx<other.posx):
            collisionsHorizontalDirection="right"
                   
    return collisionsHorizontalDirection, collisionsVerticalDirection, lastVerticalObject, lastHorizontalObject

def spriteDistance(self:pygame.sprite.Sprite,other:pygame.sprite.Sprite):
    verticalDistance=0
    horizontalDistance=0
    relativeDirection="default"
    collidingObjects=pygame.sprite.spritecollide(self,spriteGroups.allSprites,False)
    if(self.isAlive==True):
        if(not (other in collidingObjects)):
            if(self.posx>other.posx):#other is on the left
                if(other.rect.right<self.rect.left):
                    relativeDirection="left"
                    horizontalDistance=self.rect.left-other.rect.right
            elif(self.posx<other.posx): #other is on the right
                if(other.rect.left>self.rect.right):    
                    relativeDirection="right"
                    horizontalDistance=other.rect.left-self.rect.right
            if(self.posy>other.posy): #other is on the top
                if(other.rect.bottom<self.rect.top):
                    verticalDistance=self.rect.top-other.rect.bottom
            elif(self.posy<other.posy): #other is on the bottom
                if(other.rect.top>self.rect.bottom):
                    verticalDistance=other.rect.top-self.rect.top
    return horizontalDistance, verticalDistance, relativeDirection

def repeatTexture(texture:pygame.Surface,horizontalCount,verticalCount):
    textureHeight=texture.height
    textureWidth=texture.width
    subSurface=pygame.Surface((textureWidth*horizontalCount,textureHeight*horizontalCount),pygame.SRCALPHA)
    for i in range(verticalCount):
        for j in range(horizontalCount):
            subSurface.blit(texture,(j*textureWidth,i))
    return subSurface