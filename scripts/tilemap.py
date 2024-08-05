# all permutaitions of -1,0,1 in pairs
import pygame
import json

AUTOTILE_MAP = {
    # sorted to hash tuples in any order
    # tiles for all squares in a 3x3 square
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHBOUR_OFFSETS = [(-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (0,0), (-1,1), (0,1), (1,1)]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {} # only do physics here, easier to optimize if stuff is on a grid
        self.offgrid_tiles = []
        # use a dict for tilemap so that we don't need to fill empty space
        # can store location like '3;10': 'grass'
        # can use tuples but this is easier due to how files are stored
        
        # example code to populate tilemap
        # for i in range(10):
        #     # vertical line of grass from 3 to 12 at y=10
        #     self.tilemap[str(3+i) + ';10'] = {'type': 'grass', 'variant': 1, 'pos': (3+i,10)}
        #     # extract pos as tuple here because they are easier to work with
            
        #     # horizontal line
        #     self.tilemap['10;' + str(5+i)] = {'type': 'stone', 'variant': 1, 'pos': (10,5+i)}
            
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
    
    def solid_check(self, pos):
        tile_loc = str(int(pos[0]//self.tile_size)) + ';' + str(int(pos[1]//self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
    
    def render(self, surf, offset=(0,0)):
        # render offgrid tiles first because they are background
        for tile in self.offgrid_tiles:
            # offgrid_tiles contains the same thing as tilemap but in a list
            # the pos is pixels here not on the grid so we don't need to scale pos with tile_size
            surf.blit(self.game.assets[tile['type']][tile['variant']], 
                      (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
        
        
        for x in range(offset[0]//self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1]//self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                   tile = self.tilemap[loc]
                   surf.blit(self.game.assets[tile['type']][tile['variant']], 
                            (tile['pos'][0]*self.tile_size - offset[0], 
                             tile['pos'][1]*self.tile_size - offset[1])
                            ) 
        
        # non-optimized version that renders all tiles instead of only the ones on screen
        # for loc in self.tilemap:
        #     tile = self.tilemap[loc]
        #     # print(tile)
        #     # print(self.game.assets[tile['type']])
        #     surf.blit(self.game.assets[tile['type']][tile['variant']], 
        #               (tile['pos'][0]*self.tile_size - offset[0], 
        #                tile['pos'][1]*self.tile_size - offset[1])
        #             )
        
    def save(self, path):
        with open(path, 'w') as f:
            json.dump({
                'tilemap': self.tilemap,
                'size': self.tile_size,
                'offgrid': self.offgrid_tiles
            }, f)

    def load(self, path):
        with open(path, 'r') as f:
            map_data = json.load(f)
        
        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if tile['type'] not in AUTOTILE_TILES:
                continue
            neighbors = set()
            for shift in [(-1,0), (1,0), (0,1), (0,-1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if neighbors in AUTOTILE_MAP:
                tile['variant'] = AUTOTILE_MAP[neighbors]
                
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
        
        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy()) # both copies are shallow
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
        return matches
            