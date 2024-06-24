import sys
import pygame
from scripts.entities import PhysicsEntity
from scripts.utils import load_images, load_img
from scripts.tilemap import Tilemap


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
            'player': load_img('entities/player.png')
        }

        # print(self.assets)

        self.tilemap = Tilemap(self, tile_size=16)

        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))

    def run(self):
        while True:
            # fill background color and refresh screen so that img doesn't stay after movement
            self.display.fill((14, 219, 248))

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

            self.tilemap.render(self.display)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display)
            
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
                        self.player.velocity[1] = -3
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
