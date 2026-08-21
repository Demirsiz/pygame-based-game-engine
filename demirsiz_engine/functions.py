import math
import pygame
from . import spritegroups
from . import classes

def circle_collision(circle1:pygame.sprite.Sprite,circle2:pygame.sprite.Sprite):
    dx=(circle1.pos_x-circle2.pos_x)
    dy=(circle1.pos_y-circle2.pos_y)
    distance=math.sqrt((dx*dx)+(dy*dy))
    if(distance<(circle1.radius+circle2.radius)):
        if(circle1.hp>0 and circle2.hp>0):
            return(True)
        else:
            return(False)
    else:
        return(False)

def rect_collision_direction(self,other:pygame.sprite.Sprite):
    collisions_vertical_direction="default"
    collisions_horizontal_direction="default"
    
    left_overlap = self.rect.right - other.rect.left
    right_overlap= other.rect.right - self.rect.left
    top_overlap= self.rect.bottom - other.rect.top
    bottom_overlap=other.rect.bottom - self.rect.top
            
    min_overlap_x=min(left_overlap,right_overlap)
    min_overlap_y=min(top_overlap,bottom_overlap)
            
    if min_overlap_y<min_overlap_x:
        #vertical collision
        self.last_vertical_collider=other
        if(self.pos_y>other.pos_y):
            collisions_vertical_direction="up"
        elif(self.pos_y<other.pos_y):
            collisions_vertical_direction="down"
            
    elif(min_overlap_x<min_overlap_y):
        #horizontal collision
        self.last_horizontal_collider=other
        if(self.pos_x>other.pos_x):
            collisions_horizontal_direction="left"
        elif(self.pos_x<other.pos_x):
            collisions_horizontal_direction="right"
                   
    return collisions_horizontal_direction, collisions_vertical_direction

def sprite_distance(self:pygame.sprite.Sprite,other:pygame.sprite.Sprite):
    vertical_distance=0
    horizontal_distance=0
    relative_direction="default"
    colliding_objects=pygame.sprite.spritecollide(self,spritegroups.all_sprites,False)
    if(self.is_alive==True):
        if(not (other in colliding_objects)):
            if(self.pos_x>other.pos_x):#other is on the left
                if(other.rect.right<self.rect.left):
                    relative_direction="left"
                    horizontal_distance=self.rect.left-other.rect.right
            elif(self.pos_x<other.pos_x): #other is on the right
                if(other.rect.left>self.rect.right):    
                    relative_direction="right"
                    horizontal_distance=other.rect.left-self.rect.right
            if(self.pos_y>other.pos_y): #other is on the top
                if(other.rect.bottom<self.rect.top):
                    vertical_distance=self.rect.top-other.rect.bottom
            elif(self.pos_y<other.pos_y): #other is on the bottom
                if(other.rect.top>self.rect.bottom):
                    vertical_distance=other.rect.top-self.rect.top
    return horizontal_distance, vertical_distance, relative_direction

def repeat_texture(texture:pygame.Surface,horizontal_count,vertical_count):
    sub_surface=pygame.Surface((texture.get_width()*horizontal_count,texture.get_height()*horizontal_count),pygame.SRCALPHA)
    for i in range(vertical_count):
        for j in range(horizontal_count):
            sub_surface.blit(texture,(j*texture.width,i*texture.height))
    return sub_surface