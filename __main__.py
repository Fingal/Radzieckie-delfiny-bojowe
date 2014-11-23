__author__ = 'Andrzej'
import pygame
from pygame.locals import *
import configparser


class TileCache:
    """ładuje zestaw płytek"""

    def __init__(self,  width=32, height=None):
        self.width = width
        self.height = height or width
        self.cache = {}

    def __getitem__(self, filename):
        """zwraca tablicę płytek, ładuje ją jeśli potrzeba."""

        key = (filename, self.width, self.height)
        try:
            return self.cache[key]
        except KeyError:
            tile_table = self._load_tile_table(filename, self.width,
                                               self.height)
            self.cache[key] = tile_table
            return tile_table

    def _load_tile_table(self, filename, width, height):
        """ładuje obrazek i dzieli go na płytki."""
        image = pygame.image.load(filename).convert_alpha()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, int(image_width/width)):
            line = []
            tile_table.append(line)
            for tile_y in range(0, int(image_height/height)):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table
DX=[0, 1, 0, -1]
DY=[-1, 0, 1, 0]
MAP_TILE_WIDTH = 24
MAP_TILE_HEIGHT = 16
MAP_CACHE = TileCache(24, 16)
class Level(object):
    def load_file(self, filename="level.map"):
        self.map = []
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.tileset = parser.get("level", "tileset")
        self.map = parser.get("level", "map").split("\n")
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(self.map[0])
        self.height = len(self.map)
        self.items = {}
        for y, line in enumerate(self.map):
            for x, c in enumerate(line):
                if( not self.is_wall(x, y) and 'sprite' in self.key[c]) or 'special' in self.key[c]:
                    self.items[(x, y)] = self.key[c]

    def get_tile(self, x, y):
        try:

            char = self.map[y][x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}

    def get_tile(self, x, y):
        """zwraca co jest w danej pozycji na mapie."""
        x,y = int(x), int(y)
        try:
            char = self.map[y][x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}


    def get_bool(self, x, y, name):
        """sprawdza czy dana pozycja zawiera flagę name."""

        value = self.get_tile(x, y).get(name)
        return value in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')

    def is_wall(self, x, y):
        """czy jest mur?"""

        return self.get_bool(x, y, 'wall')

    def is_blocking(self, x, y):
        """czy blokuje ruch?"""

        if not 0 <= x < self.width or not 0 <= y < self.height:
            return True
        return self.get_bool(x, y, 'block')
    def render(self):
        wall = self.is_wall
        tiles = MAP_CACHE[self.tileset]
        image = pygame.Surface((self.width*MAP_TILE_WIDTH, self.height*MAP_TILE_HEIGHT))
        overlays = {}
        for map_y, line in enumerate(self.map):
            self.items={}
            for map_x, c in enumerate(line):
                if wall(map_x, map_y):
                    # Ustawia różne płytki w zależności od sąsiadów
                    if not wall(map_x, map_y+1):
                        if wall(map_x+1, map_y) and wall(map_x-1, map_y):
                            tile = 1, 2
                        elif wall(map_x+1, map_y):
                            tile = 0, 2
                        elif wall(map_x-1, map_y):
                            tile = 2, 2
                        else:
                            tile = 3, 2
                    else:
                        if wall(map_x+1, map_y+1) and wall(map_x-1, map_y+1):
                            tile = 1, 1
                        elif wall(map_x+1, map_y+1):
                            tile = 0, 1
                        elif wall(map_x-1, map_y+1):
                            tile = 2, 1
                        else:
                            tile = 3, 1
                    # dodaje obiekt zakrywający inne
                    if not wall(map_x, map_y-1):
                        if wall(map_x+1, map_y) and wall(map_x-1, map_y):
                            over = 1, 0
                        elif wall(map_x+1, map_y):
                            over = 0, 0
                        elif wall(map_x-1, map_y):
                            over = 2, 0
                        else:
                            over = 3, 0
                        overlays[(map_x, map_y)] = tiles[over[0]][over[1]]
                else:
                    try:
                        tile = self.key[c]['tile'].split(',')
                        tile = int(tile[0]), int(tile[1])
                    except (ValueError, KeyError):
                        # domyślne dla podłoża
                        tile = 0, 3
                tile_image = tiles[tile[0]][tile[1]]
                image.blit(tile_image,
                           (map_x*MAP_TILE_WIDTH, map_y*MAP_TILE_HEIGHT))
        return image, overlays

class Sprite(pygame.sprite.Sprite):
    is_player = False
    def __init__(self, pos=(0, 0), frames=None):
        super(Sprite, self).__init__()
        self.frames = frames
        self.animation = self.stand_animation()
        self.image = frames[0][0]
        self.rect = self.image.get_rect()
        self.pos = pos

    def stand_animation(self):
        while True:
            for frame in self.frames[0]:
                self.image = frame
                yield None
                yield None

    def update(self, *args):
        self.animation.__next__()

    def _get_pos(self):
        """Sprawdza pozycje na mapie."""

        return (self.rect.midbottom[0]-12)/24, (self.rect.midbottom[1]-16)/16

    def _set_pos(self, pos):
        """Ustawia pozycje na mapie."""

        self.rect.midbottom = pos[0]*24+12, pos[1]*16+16
        self.depth = self.rect.midbottom[1]

    pos = property(_get_pos, _set_pos)

    def move(self, dx, dy):
        """przesuwa go."""

        self.rect.move_ip(dx, dy)
        self.depth = self.rect.midbottom[1]


class Player(Sprite):
    is_player = True

    def __init__(self, pos=(0, 0)):
        Sprite.__init__(self, pos, TileCache()["player.png"])
        self.direction = 2
        self.image = self.frames[self.direction][0]
        self.animation = None
    def walk_animation(self):
        for frame in range(4):
            self.image = self.frames[self.direction][frame % 2]
            yield None
            self.move(3*DX[self.direction],2*DY[self.direction])
            self.move(3*DX[self.direction],2*DY[self.direction])


    def update(self, *args):
        if self.animation == None:
            self.image=self.frames[self.direction][0]
        else:
            try:
                self.animation.__next__()
            except StopIteration:
                self.animation = None
class SortedUpdates(pygame.sprite.RenderUpdates):

    def sprites(self):

        return sorted(self.spritedict.keys(), key=lambda sprite: sprite.depth)


class Button(Sprite):
    def __init__(self, pos=(0, 0)):
        pos = (pos[0],pos[1])
        Sprite.__init__(self, pos, TileCache()["button.png"])
        self.image = self.frames[0][0]
        self.status=0;
        self.animation = None
    def touch(self,level):
        self.status=(self.status+1)%2
        self.image = self.frames[0][self.status]
    def update(self, *args):
        self.animation=None


class Door(Sprite):
    def __init__(self, pos=(0, 0)):
        Sprite.__init__(self, pos, TileCache()["doors.png"])
        self.image = self.frames[0][0]
        self.status=0
        self.animation = None
    def touch(self,level):
        #print ("aaaa")
        self.status=(self.status+1)%2
        self.image = self.frames[0][self.status]
        level.get_tile(self.pos[0],self.pos[1])["block"] = str(1 - self.status)
    def update(self, *args):
        self.animation=None




class Game:
    def __init__(self):
        self.level = Level()
        self.level.load_file('level.map')
        self.width = MAP_TILE_WIDTH*self.level.width
        self.height = MAP_TILE_HEIGHT*self.level.height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.special={}
        self.load_sprite()
        self.clock=pygame.time.Clock()
        self.load_level()
        self.game_over=False
        self.pressed_key=None
    def load_sprite(self):
        sprite_cahe = TileCache(32, 32)
        self.sprites = SortedUpdates()
        for pos, tile in self.level.items.items():
            if tile.get("player") in ('true', '1', 'yes', 'on'):
                sprite = Player(pos)
                self.player = sprite
            elif tile['sprite'] in ('button'):
                sprite = Button(pos)
                if not pos in self.special.keys():
                    self.special[pos]=[]
                self.special[pos].append(sprite)
            elif tile['sprite'] in ('door'):
                sprite = Door(pos)
                poses=[]
                for i in tile['open'].split():
                    poses.append(tuple([int(s) for s in i.split(",") if s.isdigit()]))
                for i in poses:
                    if not i in self.special.keys():
                        self.special[i] = []
                    self.special[i].append(sprite)
            else:
                sprite = Sprite(pos, sprite_cahe[tile["sprite"]])
            self.sprites.add(sprite)
        print (self.special.keys())

    def load_level(self):
        self.background, overlay_dict = self.level.render()
        self.overlays = pygame.sprite.RenderUpdates()
        for (x, y), image in overlay_dict.items():
            overlay = pygame.sprite.Sprite(self.overlays)
            overlay.image = image
            overlay.rect = image.get_rect().move(x * 24, y * 16 - 16)
        self.screen.blit(self.background, (0, 0))
        self.overlays.draw(self.screen)
        pygame.display.flip()

    def walk(self, d):
        self.player.direction = d
        x,y = self.player.pos
        if not self.level.is_blocking(int(x+DX[d]), int(y+DY[d])):
            self.player.animation = self.player.walk_animation()

    def action(self):
        x, y = self.player.pos[0]+DX[self.player.direction],self.player.pos[1]+DY[self.player.direction]
        #print (x,y)
        if (x,y) in self.special.keys():
            for i in self.special[(x, y)]:
                i.touch(self.level);


    def control(self):
        if self.pressed_key == K_e:
            self.action()
        if self.pressed_key == K_w:
            self.walk(0)
        elif self.pressed_key == K_d:
            self.walk(1)
        elif self.pressed_key == K_s:
            self.walk(2)
        elif self.pressed_key == K_a:
            self.walk(3)
        self.pressed_key=None

    def game_loop(self):
        while not self.game_over:
            self.control()
            self.sprites.clear(self.screen, self.background)
            dirty = self.sprites.draw(self.screen)
            self.sprites.update()
            self.overlays.draw(self.screen)
            pygame.display.update(dirty)
            dirty = self.overlays.draw(self.screen)
            pygame.display.update(dirty)
            self.clock.tick(15)
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    self.game_over = True
                elif event.type == pygame.locals.KEYDOWN and self.player.animation == None:
                    self.pressed_key = event.key
if __name__=='__main__':
    game = Game()
    game.game_loop()