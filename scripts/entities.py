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
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])    
    
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
        
        # gravity and terminal velocity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
    def render(self, surf, offset=(0,0)):
        surf.blit(self.game.assets['player'], 
                  (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        