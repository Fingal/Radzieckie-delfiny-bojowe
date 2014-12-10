__author__ = 'Andrzej'
import pygame
from pygame.locals import *
import configparser
from line import *


def sup(a,b):
    return tuple(map(lambda x,y: x-y,a,b))

def neigbours(pos):
    x,y = pos
    return {(x,y-1),(x-1,y),(x+1,y),(x,y+1)}
def d(a,b):
    return list(zip(DX,DY)).index(sup(b,a))

class Graph:
    def __init__(self,points):
        self.graph={}
        for point in points:
            self.graph[point]=points & neigbours(point)
    def find_shortest_path(self, start, end, path=[]):
       path = path + [start]
       if start == end:
           return path
       if  start not in self.graph:
           return None
       shortest = None
       for node in self.graph[start]:
           if node not in path:
               newpath = self.find_shortest_path(node, end, path)
               if newpath:
                   if not shortest or len(newpath) < len(shortest):
                       shortest = newpath
       return shortest
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

    def front(pos,direction):
        return int(pos[0]+DX[direction]),int(pos[1]+DY[direction])
    front=staticmethod(front)
    def set_tile(self, x, y,char):
        if char in self.key.keys():
            try:
                self.map[y]=self.map[y][:x]+char+self.map[y][x+1:]
            except IndexError:
                return {}

    def get_tile(self, x, y):
        """zwraca co jest w danej pozycji na mapie."""
        x,y = int(x), int(y)
        if x<0 or y<0 or x>=len(self.map[0]) or y>=len(self.map):
            return self.key['#']

        try:
            char = self.map[y][x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}
    def get_tile_name(self, x, y):
        """zwraca co jest w danej pozycji na mapie."""
        x,y = int(x), int(y)
        try:
            return self.map[y][x]
        except IndexError:
            return ''

    def get_bool(self, x, y, name):
        """sprawdza czy dana pozycja zawiera flagę name."""

        value = self.get_tile(x, y).get(name)
        return value in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')

    def is_wall(self, x, y):
        try:
            return self.get_tile(x,y)["wall"] in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')
        except KeyError:
            return False

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
        self.direction = 0
        self.image = self.frames[self.direction][0]
        self.animation = None
    def walk(self, d,level):
        if self.direction!=d:
            self.turn(d)
        else:
            x,y = self.pos
            if not level.is_blocking(int(x+DX[d]), int(y+DY[d])):
                self.animation = self.walk_animation()
    def walk_animation(self):
        for frame in range(4):
            self.image = self.frames[self.direction][frame % 2]
            yield None
            self.move(3*DX[self.direction],2*DY[self.direction])
            self.move(3*DX[self.direction],2*DY[self.direction])

    def turn(self,d):
        self.direction=d
        self.image=self.frames[self.direction][0]

    def front(self):
        return Level.front(self.pos,self.direction)

    def update(self, *args):
        if self.animation == None:
            self.image=self.frames[self.direction][0]
        else:
            try:
                self.animation.__next__()
            except StopIteration:
                self.animation = None

    def vision(self,level):
        self.visible={}
        set={self.pos}

        for a, b in vectors((2/3)*math.pi,24,self.direction-1):
            line=Line(self.pos,a,b)
            point=line.next()
            if level.get_tile(point[0],point[1])['name']!='floor':
                    try:
                        self.visible[level.get_tile(point[0],point[1])['name']].add(point)
                    except KeyError:
                        self.visible[level.get_tile(point[0],point[1])['name']]={point}

            while not level.is_blocking(point[0],point[1]):
                set.add(point)
                point=line.next()
                try:
                    if level.get_tile(point[0],point[1])['name']!='floor':
                        try:
                            self.visible[level.get_tile(point[0],point[1])['name']].add(point)
                        except KeyError:
                            self.visible[level.get_tile(point[0],point[1])['name']]={point}
                except KeyError:
                    print(level.get_tile(point[0],point[1]))
        #print(self.visible)
        self.movable=set
        self.graph=Graph(self.movable)

    def go_to(self,point):
        if point not in self.movable:
            raise IndexError
        return self.graph.find_shortest_path(self.pos,point)

    def go_closest(self,name):
        if name not in self.visible.keys():
            raise IndexError
        paths=[]
        for pos in self.visible[name]:
            for point in (neigbours(pos) & self.movable):
                paths.append(self.graph.find_shortest_path(self.pos,point)+[pos])
        paths = [x for x in paths if len(x)>1]
        #print(paths)
        return (min(paths,key=len))

    def comand_go(self,path):
        moves=[]
        if len(path)>1:
            for start, end in zip(path[:-1],path[1:]):
                moves+=[d(start,end)]
                if len(moves)>=2 and moves[-1]!=moves[-2]:
                    moves+=moves[-1]
        return moves
    def use(self,do,what,which='closest'):
        if which=='closest':
            path=self.go_closest(what)
        else:
            path=[]
        moves=self.comand_go(path[:-1])
        direction=d(path[-2],path[-1])
        if direction!=moves[-1]:
            moves.append(direction)
        moves.append('u')
        return moves

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


class Item():
    def __init__(self,name,weight,sprite,type):
        self.name=name
        self.weight=weight
        self.sprite=sprite
        self.type=type
    def pick(self):
        self.sprite._set_pos((10000,10000))
    def drop(self,pos):
        self.sprite._set_pos(pos)



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
        self.items={}
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
        self.status={
            "hp": 100,
            "inventory": [],
            "keys": [],
            "weight": 0,
            "max_weight": 200
        }
    def load_sprite(self):
        sprite_cahe = TileCache(32, 32)
        self.sprites = SortedUpdates()
        for pos, tile in self.level.items.items():
            if tile.get("player") in ('true', '1', 'yes', 'on'):
                sprite = Player(pos)
                self.player = sprite
            elif "special" in tile.keys():
                print (tile['special'])
                if tile['special'] in ('button'):
                    sprite = Button(pos)
                    if not pos in self.special.keys():
                        self.special[pos]=[]
                    self.special[pos].append(sprite)
                elif tile['special'] in ('door'):
                    sprite = Door(pos)
                    poses=[]
                    for i in tile['open'].split():
                        poses.append(tuple([int(s) for s in i.split(",") if s.isdigit()]))
                    for i in poses:
                        if not i in self.special.keys():
                            self.special[i] = []
                        self.special[i].append(sprite)
                elif tile['special'] in ('item'):
                    sprite=Sprite(pos,sprite_cahe[tile["sprite"]])
                    self.items[pos]=Item(tile["name"],tile['weight'],sprite,self.level.get_tile_name(pos[0],pos[1]))
            else:
                print (pos)
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

    def action(self):
        x, y = self.player.front()
        #print (x,y)
        if (x,y) in self.special.keys():
            for i in self.special[(x, y)]:
                i.touch(self.level)
        if (x,y) in self.items.keys():
            self.items[(x,y)].pick()
            self.status["inventory"].append(self.items.pop((x,y)))
            self.level.set_tile(x,y,".")
            #print ("\n".join(self.level.map))

    def drop(self):
        if len(self.status["inventory"])>0:
            x, y = self.player.front()
            if not self.level.is_blocking(x,y):
                droped=self.status["inventory"].pop(0)
                self.items[(x,y)]=droped
                droped.drop((x,y))
                self.level.set_tile(x,y,droped.type)
                #print ("\n".join(self.level.map))


    def control(self):
        if self.pressed_key == K_e:
            self.action()
        if self.pressed_key == K_i:
            print (list(map(lambda i: i.name, self.status["inventory"])))
        if self.pressed_key == K_r:
            self.drop()
        if self.pressed_key == K_w:
            self.player.walk(0,self.level)
        elif self.pressed_key == K_d:
            self.player.walk(1,self.level)
        elif self.pressed_key == K_s:
            self.player.walk(2,self.level)
        elif self.pressed_key == K_a:
            self.player.walk(3,self.level)
        elif self.pressed_key == K_g:
            print(self.player.go_closest('crate'))
            print(self.player.comand_go(self.player.go_closest('crate'))[:-1])
            print(self.player.use('pick','crate'))
        elif self.pressed_key == K_v:
            print(self.player.movable)
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
            self.player.vision(self.level)
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    self.game_over = True
                elif event.type == pygame.locals.KEYDOWN and self.player.animation == None:
                    self.pressed_key = event.key
if __name__=='__main__':
    game = Game()
    game.game_loop()