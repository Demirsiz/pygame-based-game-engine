import pygame
from . import spritegroups
from . import functions

SCALE_FACTOR=3

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
        is_alive=True,
        jump_str=1,
        g=2000,
        can_fall=True,
        can_wall_jump=False,
        dying_sprite=None,
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
        self.base_spd=spd
        self.jump_str=jump_str
        self.shape=shape
        self.dying_sprite=dying_sprite

        self.death_duration=1
        self.death_timer=self.death_duration
        self.is_dying=False
        self.is_alive=True
        self.is_jumping=False
        self.is_falling=False
        self.is_sprinting=False
        self.vertical_velocity=0
        self.g=g
        self.is_grounded=False
        self.can_fall=can_fall
        self.can_wall_jump=can_wall_jump
        self.facing="default"
        self.texture=self.image
        self.stop=False
        self.last_vertical_collider=None
        self.last_horizontal_collider=None
           
    def initial_draw(self):
        if(self.shape==1):
            self.image=pygame.Surface((2*self.radius,2*self.radius),pygame.SRCALPHA)
            self.image.fill((0,0,0,0))
            pygame.draw.circle(self.image,self.color,(self.radius,self.radius),self.radius)
        elif(self.shape==2):
            if(self.texture==None):
                self.image=pygame.Surface((self.width,self.length),pygame.SRCALPHA)
                self.image.fill((0,0,255,100))
                self.texture=self.image
            else:
                self.image=self.texture
        self.rect=self.image.get_rect()
        self.rect.center=(self.pos_x,self.pos_y)
    
    def __str__(self):
        return self.name
        
    def use_attack(self,other):
        if((self.type>0 and self.is_alive==True) and other.is_alive):
            other.hp=other.hp-self.dmg
            if(other.hp<=0):              
                other.kill()
                print(f"{self} attacked {other}, dealing a damage of {self.dmg}, killing {other}.")
            else:
                print(f"{self} attacked {other}, dealing a damage of {self.dmg}. {other}'s new hp is {other.hp}")

    def walk(self,direction,dt):
        
        self.blocked_directions=self.check_collision(spritegroups.solid_objects)
        # clipping into walls issue resolved by making the mob clip into wall by exactly 1 pixel
        if(direction=="up"):
            if("up" not in self.blocked_directions):
                self.pos_y -= self.spd * dt
                self.rect.center=(self.pos_x,self.pos_y)
            else:
                self.rect.top=self.last_vertical_collider.rect.bottom-1
                self.pos_y=self.rect.centery
                    
        if(direction=="down"): 
            if("down" not in self.blocked_directions):
                self.pos_y += self.spd * dt
                self.rect.center=(self.pos_x,self.pos_y)
            else:
                self.rect.bottom=self.last_vertical_collider.rect.top+1
                self.pos_y=self.rect.centery
                       
        if(direction=="left"):
            self.facing="left"
            if("left" not in self.blocked_directions):
                self.pos_x -= self.spd * dt
                self.rect.center=(self.pos_x,self.pos_y)
            else:
                self.rect.left=self.last_horizontal_collider.rect.right-1
                self.pos_x=self.rect.centerx
        
        if(direction=="right"):
            self.facing="right"
            if("right" not in self.blocked_directions):
                self.pos_x += self.spd * dt
                self.rect.center=(self.pos_x,self.pos_y)
            else:
                self.rect.right=self.last_horizontal_collider.rect.left+1
                self.pos_x=self.rect.centerx
                
        #print(self.blocked_directions)
        self.blocked_directions.clear()

    def jump(self):
        #print("jump")
        blocked_directions=self.check_collision(spritegroups.solid_objects)
        if("down" in blocked_directions):  
            self.vertical_velocity= -self.jump_str
            self.is_jumping=True
            self.is_falling=False
            
        if(self.can_wall_jump==True and self.vertical_velocity>500):
            #print("Wall jump checked. Blocked directions:", blocked_directions)
            if(getattr(self.last_horizontal_collider,"is_wall_jumpable",False)):
                if("left" in blocked_directions or "right" in blocked_directions):
                    self.vertical_velocity= -self.jump_str
                    self.is_jumping=True
                    self.is_falling=False
            
    def sprint(self,toggle=True):
        if(self.is_grounded):
            if(toggle==True):
                if(self.is_sprinting==False):
                    self.spd=2*self.spd
                    self.is_sprinting=True
            else:
                self.spd=self.base_spd
                self.is_sprinting=False
            
    def check_collision(self,sprite_group):
        list_of_colliding_solid_objects=pygame.sprite.spritecollide(self,sprite_group,False)
        blocked_directions=[]
        
        for object in list_of_colliding_solid_objects:
            collisions_horizontal_direction , collisions_vertical_direction = functions.rect_collision_direction(self,object)
            blocked_directions.append(collisions_horizontal_direction)
            blocked_directions.append(collisions_vertical_direction)
            
        if("down"in blocked_directions):
            self.is_grounded=True
            
        return blocked_directions

    def update(self,dt):
        if(self.is_dying==True):
            #print(f"[{self.name}] Updating while dying... image id is: {id(self.image)}")
            if(self.death_timer>0):
                self.death_timer-=dt
            else:
                self.death_timer=0
                self.kill()
                
        if(self.is_jumping==True):
            self.vertical_velocity+=dt*self.g
            self.pos_y+=self.vertical_velocity*dt
            self.rect.center=(self.pos_x,self.pos_y)
            blocked_directions=self.check_collision(spritegroups.solid_objects)
            if(self.vertical_velocity<0 and "up" in blocked_directions):
                self.pos_y-=self.vertical_velocity*dt
                self.rect.center=(self.pos_x,self.pos_y)
                self.vertical_velocity=0
                self.is_jumping=False
                self.is_falling=True
            if(self.vertical_velocity>0):
                self.is_jumping=False
                self.is_falling=True
                
        blocked_directions=self.check_collision(spritegroups.solid_objects)
        if("down" not in blocked_directions and self.can_fall==True):
            if(self.is_jumping==False): 
                self.is_falling=True
            self.is_grounded=False
            
        if(self.is_falling==True):
            self.vertical_velocity+=dt*self.g
            blocked_directions=self.check_collision(spritegroups.solid_objects)
            #print(blocked_directions)
            if(self.vertical_velocity>0 and "down" in blocked_directions):
                if(self==self.last_vertical_collider):
                    self.rect.bottom=self.last_vertical_collider.rect.bottom
                else:
                    self.rect.bottom=self.last_vertical_collider.rect.top+1
                    self.pos_y=self.rect.centery
                    self.vertical_velocity=0
                    self.is_falling=False
                self.is_grounded=True
            else:
                self.pos_y+=self.vertical_velocity*dt
                self.rect.center=(self.pos_x,self.pos_y)
            
    def kill(self):
        #print(f"[{self.name}] KILL CALLED! Old image id: {id(self.image)}")
        if(self.is_dying==False):
            self.is_dying=True
            self.is_alive=False
        self.hp=0
        self.image.fill((0,0,0,0))
        if(self.shape==1):
            pygame.draw.circle(self.image,(255,0,0,100),(self.radius,self.radius),self.radius)
        elif(self.shape==2):
            if(self.dying_sprite==None):
                self.dying_sprite=pygame.Surface(self.rect.size,pygame.SRCALPHA)
                self.dying_sprite.fill((255,0,0,100))
            self.image=self.dying_sprite
        #print(f"[{self.name}] New red image id: {id(self.image)}")
        
        if(self.death_timer==0):
            pygame.sprite.Sprite.kill(self)
            self.is_dying=False

class Wall(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y,width,height,color="yellow",is_wall_jumpable=False,texture=None,texture_dest=(0,0,0,0)):
        pygame.sprite.Sprite.__init__(self)
        
        self.pos_x=pos_x
        self.pos_y=pos_y
        self.texture=texture
        self.is_wall_jumpable=is_wall_jumpable
        self.width=width
        self.height=height
        self.rect=pygame.Rect(pos_x,pos_y,width,height)
        self.texture=texture
        #going to leave both self.width/height and self.rect.width/height
        #cause i dont remember what would it break
        #just going to continue writing stuff with rect.width from now on
        
        if(self.texture==None):
            self.image=pygame.Surface((self.width,self.height),pygame.SRCALPHA)
            self.image.fill(color)
            self.texture=self.image
        else:
            self.image=functions.repeat_texture(self.rect,self.texture,texture_dest)
        
        self.rect.topleft=(self.pos_x,self.pos_y)
        
    def udpate(self):
        self.image=functions.repeat_texture(self.rect,self.texture)
        
class Weapon(pygame.sprite.Sprite):
    def __init__(self,name, dmg, cooldown, owner, range=25, type=1, attack_duration=0.3):
        pygame.sprite.Sprite.__init__(self)  
        
        self.name=name
        self.dmg=dmg
        self.range=range
        self.cooldown=cooldown
        self.owner=owner
        self.type=type     
        self.attack_duration=attack_duration
        
        self.is_ready=True
        self.is_attacking=False
        self.cooldown_timer=self.cooldown
        self.attack_timer=self.attack_duration
        

        if(self.texture==None):
            self.image=pygame.Surface((range,10),pygame.SRCALPHA)
            self.image.fill((0,0,100))
            self.texture=self.image
        else:
            self.image=self.texture
        self.rect=self.image.get_rect()
        self.range=self.rect.width-5
        self.image.set_alpha(0)
        
    def __str__(self):
        return self.name
        
    def update(self,dt):
        if(self.is_ready==False):
            self.cooldown_timer-=dt
            if(self.cooldown_timer<=0):
                self.is_ready=True
                self.cooldown_timer=self.cooldown
                
        if(self.is_attacking==True):
            self.attack_timer-=dt
            self.image.set_alpha(255)
            if(self.owner.facing=="right"):
                self.image=self.texture
                self.rect.topleft=(self.owner.rect.right-5,self.owner.pos_y+5)
            elif(self.owner.facing=="left"): 
                self.image=pygame.transform.flip(self.texture,True,False)
                self.rect.topright=(self.owner.rect.left+5,self.owner.pos_y+5)
            if(self.attack_timer<=0):
                self.image.set_alpha(0)
                self.is_attacking=False
                self.attack_timer=self.attack_duration
            
            
    def use_attack(self,owner,other):
            if(self.is_ready==True):
                horizontal_distance, vertical_distance, relative_direction=functions.spriteDistance(owner,other)
                self.is_ready=False
                self.is_attacking=True
                self.cooldown_timer=self.cooldown
                #print("usedattack")
                #print(relative_direction)
                if(relative_direction==owner.facing):
                    if(horizontal_distance<=self.range and vertical_distance<=0):
                        if(other.is_alive==True):
                            other.hp=other.hp-self.dmg
                            #print("damaged")
                            if(other.hp<=0):
                                other.kill()
                                print(f"{owner} attacked {other} using {self}, dealing a damage of {self.dmg}, killing {other}.")
                            else:
                                print(f"{owner} attacked {other} using {self}, dealing a damage of {self.dmg}. {other}'s new hp is {other.hp}")
            
class SpriteSheet(pygame.sprite.Sprite):
    def __init__(self,file_path):
        self.file_path=file_path
        self.sprite_sheet=pygame.image.load(file_path).convert_alpha()
    def get_sprite(self,pos_x,pos_y,width,height):
        raw_sprite=pygame.Surface((width,height),pygame.SRCALPHA)
        print(raw_sprite.get_rect())
        raw_sprite.blit(self.sprite_sheet,area=(pos_x,pos_y,width,height))
        sprite=pygame.transform.scale(raw_sprite,(width*SCALE_FACTOR,height*SCALE_FACTOR))
        return sprite
    