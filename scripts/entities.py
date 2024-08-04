import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        # want list here so that if we spawn multiple entities at the same position they don't have the same reference to the position
        # also incase we pass a tuple  
        # can also use pygama.math.Vector2 instead
        self.pos = list(pos)
        self.size = size
        self.velocity = [0,0]
        self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}
        
        self.action = ''
        # padding because the images are slightly larger than the hitbox
        # would need different values for each entity usually, but can get away with this for now
        self.anim_offset = (-3,-3) 
        self.flip = False
        self.set_action('idle')
        self.last_movement = [0,0]
        
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])  
    
    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
            
    def set_flip(self, flip):
        self.flip = flip
    
    def update(self, tilemap, movement=(0,0)):
        self.collisions = {'left': False, 'right': False, 'up': False, 'down': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                
                # why not use Rect for physical entity instead of position?
                # because Rect only allows integer values so movement += 0.5 has no effect
                # can use pygame-ce's FRECT instead, which allows float values
                self.pos[0] = entity_rect.x
                
                    
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        if movement[0] < 0:
            self.flip = True
        elif movement[0] > 0:
            self.flip = False
        self.last_movement = movement
        
        # gravity and terminal velocity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
            
        # friction in x axis
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        elif self.velocity[0] < 0:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
            
        self.animation.update()
        
    def render(self, surf, offset=(0,0)):
        # decide if we want to flip image before rendering it
        # flip(img, h_flip, v_flip)
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0], 
                   self.pos[1] - offset[1] + self.anim_offset[1]))
        
        # surf.blit(self.game.assets['player'], 
        #           (self.pos[0] - offset[0], self.pos[1] - offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.MAX_JUMPS = 2
        self.jumps = self.MAX_JUMPS
        self.wall_slide = False
        
    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement)
        
        self.air_time+=1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = self.MAX_JUMPS
        
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        if self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
        