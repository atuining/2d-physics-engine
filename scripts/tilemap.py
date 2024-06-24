# all permutaitions of -1,0,1 in pairs
import pygame

NEIGHBOUR_OFFSETS = [(-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (0,0), (-1,1), (0,1), (1,1)]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {} # only do physics here, easier to optimize if stuff is on a grid
        self.offgrid_tiles = []
        # use a dict for tilemap so that we don't need to fill empty space
        # can store location like '3;10': 'grass'
        # can use tuples but this is easier due to how files are stored
        
        for i in range(10):
            # vertical line of grass from 3 to 12 at y=10
            self.tilemap[str(3+i) + ';10'] = {'type': 'grass', 'variant': 1, 'pos': (3+i,10)}
            # extract pos as tuple here because they are easier to work with
            
            # horizontal line
            self.tilemap['10;' + str(5+i)] = {'type': 'stone', 'variant': 1, 'pos': (10,5+i)}
            
    # get tiles around a given pixel position
    def tiles_around(self, pos):
        tiles = []
        # convert the pixel position into a grid position
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        # check all neighbouring tiles
        for offset in NEIGHBOUR_OFFSETS:
            check_loc =  str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
            
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0]*self.tile_size, tile['pos'][1]*self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def render(self, surf):
        # render offgrid tiles first because they are background
        for tile in self.offgrid_tiles:
            # offgrid_tiles contains the same thing as tilemap but in a list
            # the pos is pixels here not on the grid so we don't need to scale pos with tile_size
            surf.blit(self.game.assets[tile['type']][tile['variant']],tile['pos'])
        
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            # print(tile)
            # print(self.game.assets[tile['type']])
            surf.blit(self.game.assets[tile['type']][tile['variant']], 
                      (tile['pos'][0]*self.tile_size, 
                       tile['pos'][1]*self.tile_size)
                    )
        
        
    
            