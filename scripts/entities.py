import pygame
import math
import random
from scripts.particle import Particle
from scripts.spark import Spark


class PhysicsEntity:

    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        # want list here so that if we spawn multiple entities at the same position they don't have the same reference to the position
        # also incase we pass a tuple
        # can also use pygama.math.Vector2 instead
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }

        self.action = ''
        # padding because the images are slightly larger than the hitbox
        # would need different values for each entity usually, but can get away with this for now
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0],
                           self.size[1])

    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' +
                                              self.action].copy()

    def set_flip(self, flip):
        self.flip = flip

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }

        frame_movement = (movement[0] + self.velocity[0],
                          movement[1] + self.velocity[1])

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

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        # decide if we want to flip image before rendering it
        # flip(img, h_flip, v_flip)
        surf.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
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
        self.dashing = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)

        self.air_time += 1
        
        if self.air_time > 120:
            self.game.dead += 1
        
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = self.MAX_JUMPS

        self.wall_slide = False
        if (self.collisions['right']
                or self.collisions['left']) and self.air_time > 4:
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

        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                speed = random.random() * 0.5 + 0.5
                angle = random.random() * math.pi * 2
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(
                    Particle(self.game,
                             'particle',
                             self.rect().center,
                             velocity=pvelocity,
                             frame=random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        elif self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = 8 * abs(self.dashing) / self.dashing
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [
                3 * random.random() * abs(self.dashing) / self.dashing, 0
            ]
            self.game.particles.append(
                Particle(self.game,
                         'particle',
                         self.rect().center,
                         velocity=pvelocity,
                         frame=random.randint(0, 7)))

        # friction in x axis
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        elif self.velocity[0] < 0:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    # do not render player for first 10 frames of dash animation
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset)

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

    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60


class Enemy(PhysicsEntity):

    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            tile_ahead = tilemap.solid_check(
                (self.rect().centerx + (-7 if self.flip else 7),
                 self.pos[1] + 23))
            if tile_ahead and not (self.collisions['left']
                                   or self.collisions['right']):
                movement = ((movement[0] - 0.5) if self.flip else
                            (movement[0] + 0.5), movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            # spawn projectile when enemy stops
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0],
                       self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if self.flip and dis[0] < 0:
                        self.game.projectiles.append(
                            [[self.rect().centerx - 7,
                              self.rect().centery], -1.5, 0])
                        for _ in range(4):
                            self.game.sparks.append(
                                Spark(self.game.projectiles[-1][0],
                                      random.random() - 0.5 + math.pi,
                                      2 + random.random()))
                    if not self.flip and dis[0] > 0:
                        self.game.projectiles.append(
                            [[self.rect().centerx + 7,
                              self.rect().centery], 1.5, 0])
                        for _ in range(4):
                            self.game.sparks.append(
                                Spark(self.game.projectiles[-1][0],
                                      random.random() - 0.5,
                                      2 + random.random()))
        # walk randomly every 6-7 seconds
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # kill enemy if player collides while in initial frames of dashing
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                for _ in range(30):
                    angle = random.random() * 2 * math.pi
                    speed = random.random() * 5
                    self.game.sparks.append(
                        Spark(self.rect().center, angle,
                              2 + random.random()))
                    self.game.particles.append(
                        Particle(
                            self.game,
                            'particle',
                            self.rect().center,
                            velocity=[
                                math.cos(math.pi + angle) * speed * 0.5,
                                math.sin(math.pi + angle) * speed * 0.5
                            ],
                            frame=random.randint(0, 7),
                        ))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True

    # render gun
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        if self.flip:
            surf.blit(
                pygame.transform.flip(self.game.assets['gun'], True, False),
                (self.rect().centerx -
                 4 - self.game.assets['gun'].get_width() - offset[0],
                 self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'],
                      (self.rect().centerx + 4 - offset[0],
                       self.rect().centery - offset[1]))
