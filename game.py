import random
import sys
import math
import pygame
from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_images, load_img, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle

class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640, 480))
        
        # scale things so player is larger, i.e. render stuff on display then scaling it up 
        # to the screen creates the pixel effect
        self.display = pygame.Surface((320,240))

        self.clock = pygame.time.Clock()
        self.movement = [False, False]

        # # wanna use png images usually because they are lossless
        # self.img = pygame.image.load('data/images/clouds/cloud_1.png')

        # self.img.set_colorkey((0, 0, 0))  # set background to be transparent

        # self.img_pos = [160, 260]

        # # collision physics
        # self.collision_area = pygame.Rect(50, 50, 300, 50)

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_img('entities/player.png'),
            'background': load_img('background.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
        }

        # print(self.assets)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')
        
        self.player = Player(self, (50, 50), (8, 15))

        self.scroll = [0, 0] # camera's location
        
        # spawn leaf particles from trees
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
        self.particles = []
        
    def run(self):
        while True:
            # fill background color and refresh screen so that img doesn't stay after movement
            #self.display.fill((14, 219, 248))

            # # splat operator to unpack the list into the rectangle
            # # otherwise use self.img_pos[0] and self.img_pos[1] for the top left corner of the rectangle
            # # and self.img.get_width() and self.img.get_height() for the width and height of the image
            # img_r = pygame.Rect(*self.img_pos, *self.img.get_size())

            # if img_r.colliderect(self.collision_area):
            #     pygame.draw.rect(self.screen, (0, 100, 255),self.collision_area)
            # else:
            #     pygame.draw.rect(self.screen, (0, 50, 155), self.collision_area)

            # # put img here so that it is drawn on top of the collision area
            # self.img_pos[1] += (self.movement[1] - self.movement[0]) * 5
            # # blit = putting one memory copy on another
            # self.screen.blit(self.img, self.img_pos)

            self.display.blit(self.assets['background'], (0,0))
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0])/30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1])/30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for rect in self.leaf_spawners:
                # random.random() = [0,1) times 49999 here so rate of spawning is lower
                # and positively correlated to size of rect
                if random.random() * 49999 < rect.width * rect.height:
                    # linearly distribute spawning on width and height of rect
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset = render_scroll)
            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    # add a sway to the particles
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            
            # print(self.tilemap.tiles_around(self.player.pos))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(
                60)  # a dynamic sleep so that the window runs at 60 fps


Game().run()
