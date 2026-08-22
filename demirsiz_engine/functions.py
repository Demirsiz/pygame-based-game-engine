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

def repeat_texture(canvas:pygame.Rect,texture:pygame.Surface,dest:pygame.Rect=(0,0,0,0)):
    #if a dest rect is defined it selects which part of object is gonna be texture painted (xofset,yofset,width,height)
    destination=pygame.Rect(dest)
    if(destination.width==0):
        width=canvas.width
    else:
        width=destination.width
    if(destination.height==0):
        height=canvas.height
    else:
        height=destination.height
    
    texture_width=texture.get_width()
    texture_height=texture.get_height()
    #print(texture_height)
    #print(texture_width)
    offset_x=destination.left
    offset_y=destination.top
    
    horizontal_count=width//texture_width
    vertical_count=height//texture_height
    #floor divisions to find how many whole texture parts are gonna be blitted
    
    width_remainder=width%texture_width
    height_remainder=height%texture_height
    #print(width_remainder)
    #print(height_remainder)
    
    bottom_slice=pygame.Surface.subsurface(texture,(0,0,texture_width,height_remainder))
    right_slice=pygame.Surface.subsurface(texture,(0,0,width_remainder,texture_height))
    corner_slice=pygame.Surface.subsurface(texture,(0,0,width_remainder,height_remainder))
    #partial parts of the textures to complete remaining parts
    
    sub_surface=pygame.Surface((width,height),pygame.SRCALPHA)
    
    for i in range(vertical_count):
        for j in range(horizontal_count):
            sub_surface.blit(texture,(j*texture_width+offset_x,i*texture_height+offset_y))
        sub_surface.blit(right_slice,(horizontal_count*texture_width+offset_x,i*texture_height+offset_y))
    
    for k in range(horizontal_count):
        sub_surface.blit(bottom_slice,(texture_width*k+offset_x,texture_height*vertical_count+offset_y))
        
    sub_surface.blit(corner_slice,(texture_width*horizontal_count+offset_x,texture_height*vertical_count+offset_y))
        
    return sub_surface

def calculate_borders(screen,border_thickness,border_texture=None):
    top_border=classes.Wall(0,0,screen.get_width(),border_thickness,is_wall_jumpable=True,texture=border_texture)
    bottom_border=classes.Wall(0,screen.get_height()-border_thickness,screen.get_width(),border_thickness,is_wall_jumpable=True,texture=border_texture)
    left_border=classes.Wall(0,0,border_thickness,screen.get_height(),is_wall_jumpable=True,texture=pygame.transform.rotate(border_texture,90))
    right_border=classes.Wall(screen.get_width()-border_thickness,0,border_thickness,screen.get_height(),is_wall_jumpable=True,texture=pygame.transform.rotate(border_texture,90))

    return (top_border,bottom_border,left_border,right_border)