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
        
    def update(self, movement=(0,0)):
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.pos[0] += frame_movement[0]
        self.pos[1] += frame_movement[1]
        
    def render(self, surf):
        surf.blit(self.game.assets['player'], self.pos)
        