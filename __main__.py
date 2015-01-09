__author__ = 'Andrzej'
import pygame
from inputbox import Inputbox
from pygame.locals import *
import configparser
from line import *
from Exception import *

def sup(a,b):
    return tuple(map(lambda x,y: x-y,a,b))

def add(a,b):
    return tuple(map(lambda x,y: x-y,a,b))


def neigbours(pos):
    x,y = pos
    return {(x,y-1),(x-1,y),(x+1,y),(x,y+1)}

def d(a,b):
    return list(zip(DX,DY)).index(sup(b,a))

def distance(a,b):
    x,y=sup(a,b)
    return abs(x)+abs(y)

class Graph:
    def __init__(self,points):
        self.graph={}
        for point in points:
            self.graph[point]=points & neigbours(point)
    def bfs_paths(self, start, goal):
        queue = [(start, [start])]
        while queue:
            (vertex, path) = queue.pop(0)
            for next in self.graph[vertex] - set(path):
                if next == goal:
                    yield path + [next]
                else:
                    queue.append((next, path + [next]))
    def find_shortest_path(self, start, goal):
        try:
            return next(self.bfs_paths(start, goal))
        except StopIteration:
            return None

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
    directions={
        "polnoc":0,
        "wschod":1,
        "polodnie":2,
        "zachod":3
    }
    def __init__(self, level, pos=(0, 0)):
        Sprite.__init__(self, pos, TileCache()["player.png"])
        self.level=level
        self.visible={}
        self.items={}
        self.memory=set()
        self.direction = 0
        self.image = self.frames[self.direction][0]
        self.animation = None
        self.action=False

    def walk(self, d):
        if self.direction!=d:
            self.turn(d)
        else:
            x,y = self.pos
            x,y=int(x+DX[d]), int(y+DY[d])
            if not self.level.is_blocking(x,y):
                self.animation = self.walk_animation()
                self.action = True
            else:
                self.memory= self.memory - {(x,y)}
                raise Task_Failure("ścieźka jest zablokowana, zgubiłem się")

    def walk_animation(self):
        for frame in range(4):
            self.image = self.frames[self.direction][frame % 2]
            yield None
            self.move(3*DX[self.direction],2*DY[self.direction])
            self.move(3*DX[self.direction],2*DY[self.direction])

    def rotate(self, direction):
        try:
            self.turn(self.directions[direction])
        except KeyError:
            if direction=='prosto':
                self.turn(self.direction)
            elif direction=='prawo':
                self.turn(self.direction+1)
            elif direction=='tyl':
                self.turn(self.direction+2)
            elif direction=='lewo':
                self.turn(self.direction+3)
            else:
                raise Task_Failure("Nieodpowiedni kierunek")

    def turn(self,d):
        self.direction=d%4
        self.image=self.frames[self.direction][0]
        self.vision()

    def front(self):
        return Level.front(self.pos,self.direction)

    def update(self, *args):
        if self.animation == None:
            self.image=self.frames[self.direction][0]
        else:
            try:
                self.animation.__next__()
            except StopIteration:
                self.action=False
                self.animation = None

    def in_front(self,poses):
        x,y =DX[self.direction],DY[self.direction]
        if x==0:
            return {item for item in poses if abs(item[0]-self.pos[0])<=1 and item[1]*y>self.pos[1]*y}
        if y==0:
            return {item for item in poses if abs(item[1]-self.pos[1])<=1 and item[0]*x>self.pos[0]*x}
    def in_left(self,poses):
        x,y =DX[self.direction],DY[self.direction]
        if x==0:
            return {item for item in poses if y*(item[0]-self.pos[0])>1}
        if y==0:
            return {item for item in poses if -x*(item[1]-self.pos[1])>1}
    def in_right(self,poses):
        x,y =DX[self.direction],DY[self.direction]
        if x==0:
            return {item for item in poses if -y*(item[0]-self.pos[0])>1}
        if y==0:
            return {item for item in poses if x*(item[1]-self.pos[1])>1}

    def vision(self):
        self.visible={}
        set={self.pos}

        for a, b in vectors((2/3)*math.pi,24,self.direction-1):
            line=Line(self.pos,a,b)
            point=line.next()
            if self.level.get_tile(point[0],point[1])['name']!='floor':
                try:
                    self.visible[self.level.get_tile(point[0],point[1])['name']].add(point)
                except KeyError:
                    self.visible[self.level.get_tile(point[0],point[1])['name']]={point}
                try:
                    self.items[self.level.get_tile(point[0],point[1])['name']].add(point)
                except KeyError:
                    self.items[self.level.get_tile(point[0],point[1])['name']]={point}

            while not self.level.is_blocking(point[0],point[1]):
                set.add(point)
                point=line.next()
                try:
                    if self.level.get_tile(point[0],point[1])['name']!='floor':
                        try:
                            self.visible[self.level.get_tile(point[0],point[1])['name']].add(point)
                        except KeyError:
                            self.visible[self.level.get_tile(point[0],point[1])['name']]={point}
                        try:
                            self.items[self.level.get_tile(point[0],point[1])['name']].add(point)
                        except KeyError:
                            self.items[self.level.get_tile(point[0],point[1])['name']]={point}
                except KeyError:
                    pass
        #print(self.visible)
        self.movable=set
        self.memory=self.memory | self.movable
        self.graph=Graph(self.memory)

    def go_to(self,point):
        if point not in self.movable:
            raise Task_Failure("Nie mogę znaleźć drogi do tego miejsca")
        return self.graph.find_shortest_path(self.pos,point)

    def go_closest(self,name,which='wszystkie'):
        if which=="wszystkie":
            visible=self.items
        else:
            visible=self.visible
        if name not in visible.keys():
            raise Task_Failure("Nie widzę niczego takiego")
        elif not visible[name]:
            raise Task_Failure("Nie widzę niczego takiego")
        paths=[]
        for pos in visible[name]:
            for point in (neigbours(pos) & self.memory):
                if point==self.pos:
                    return [pos]
                try:
                    paths.append(self.graph.find_shortest_path(self.pos,point)+[pos])
                except TypeError:
                    pass
        #print(paths)
        if len(paths)==0:
            raise Task_Failure("Nie mogę znaleźć ścieżki")
        return (min(paths,key=len))

    def comand_go(self,path):
        moves=[]
        if len(path)>1:
            for start, end in zip(path[:-1],path[1:]):
                moves+=[d(start,end)]
                if len(moves)>=2 and moves[-1]!=moves[-2]:
                    moves+=[moves[-1]]
                elif len(moves)==1 and moves[0]!=self.direction:
                    moves+=[moves[0]]
        return moves
    def use(self,do,what,all,which='closest'):
        if which=='closest':
            path=self.go_closest(what,all)
        else:
            path=[]
        moves=self.comand_go(path[:-1])
        if do=='idz':
            return moves
        try:
            direction=d(path[-2],path[-1])
            if direction!=moves[-1]:
                moves.append(direction)
        except:
            self.turn(d(self.pos,path[0]))
        if do=='uzyj':
            moves.append('a')
        elif do=='wez':
            moves.append('u')
        return moves
    def go_straight(self,how_far):
        if how_far==0:
            point=[self.pos[0]+DX[self.direction],self.pos[1]+DY[self.direction]]
            while not self.level.is_blocking(point[0],point[1]):
                point=[point[0]+DX[self.direction],point[1]+DY[self.direction]]
                how_far+=1
        return [self.direction]*int(how_far)


class SortedUpdates(pygame.sprite.RenderUpdates):

    def sprites(self):

        return sorted(self.spritedict.keys(), key=lambda sprite: sprite.depth)


class Button(Sprite):
    def __init__(self, pos=(0, 0)):
        pos = (pos[0],pos[1])
        Sprite.__init__(self, pos, TileCache()["button.png"])
        self.image = self.frames[0][0]
        self.status=0
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
        self.screen = pygame.display.set_mode((self.width, self.height+160))
        self.inputbox=Inputbox(40,self.screen)
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
        self.waiting=True
    def load_sprite(self):
        sprite_cahe = TileCache(32, 32)
        self.sprites = SortedUpdates()
        for pos, tile in self.level.items.items():
            if tile.get("player") in ('true', '1', 'yes', 'on'):
                sprite = Player(self.level,pos)
                self.player = sprite
            elif "special" in tile.keys():
                #print (tile['special'])
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

    def pick(self):
        x, y = self.player.front()
        if (x,y) in self.items.keys():
            self.items[(x,y)].pick()
            self.player.items[self.items[(x,y)].name].remove((x,y))
            self.status["inventory"].append(self.items.pop((x,y)))
            self.level.set_tile(x,y,".")
            #print ("\n".join(self.level.map))
        else:
            raise Task_Failure("nie da sie tego podnieść")

    def drop(self,name):
        droppable=[i for i in self.status["inventory"] if i.name==name]
        #print(droppable)
        if droppable:
            x, y = self.player.front()
            if not self.level.is_blocking(x,y):
                dropped=droppable[0]
                self.status["inventory"].remove(dropped)
                self.items[(x,y)]=dropped
                dropped.drop((x,y))
                self.level.set_tile(x,y,dropped.type)
                #print ("\n".join(self.level.map))
            else:
                raise Task_Failure("nie mogę tu odłożyć przedmiotu")
        else:
            raise Task_Failure("nie mam takiego przedmiotu")

    def recognize(self,comands):
        try:
            if comands[0]=="wez":
                do,what = comands[0:2]
                try:
                    which=comands[2]
                except:
                    which='wszystkie'
                return self.player.use(do,what,which)
            elif comands[0]=="idz":
                if comands[1]=='do':
                    try:
                        return self.player.use('idz',comands[2],comands[3])
                    except IndexError:
                        return self.player.use('idz',comands[2],'widoczne')
                else:
                    where,how_far=comands[-1],int(comands[1])
                    self.player.rotate(where)
                    return self.player.go_straight(how_far)
            elif comands[0]=="obrot":
                self.player.rotate(comands[1])
            elif comands[0]=="odloz":
                try:
                    self.drop(comands[1])
                except KeyError:
                    raise Task_Failure("nie mam tego w ekwipunku")
            elif comands[0]=="uzyj":
                try:
                    return self.player.use('uzyj',comands[1],comands[2])
                except IndexError:
                    return self.player.use('uzyj',comands[1],'widoczne')
            else:
                self.inputbox.next("nie rozumiem")
            return []
        except Task_Failure as message:
            self.inputbox.next(str(message))
            return []

    def control(self):
        if self.pressed_key == 'u':
            self.pick()
        if self.pressed_key == 'a':
            self.action()
        if self.pressed_key == K_i:
            print (list(map(lambda i: i.name, self.status["inventory"])))
        if self.pressed_key == 0:
            self.player.walk(0,)
        elif self.pressed_key == 1:
            self.player.walk(1,)
        elif self.pressed_key == 2:
            self.player.walk(2,)
        elif self.pressed_key == 3:
            self.player.walk(3,)
        elif self.pressed_key == K_g:
            print(self.player.go_closest('crate'))
            print(self.player.comand_go(self.player.go_closest('crate'))[:-1])
            print(self.player.use('pick','crate'))
        elif self.pressed_key == K_v:
            print(self.player.movable)
        self.pressed_key=None

    def game_loop(self):
        while not self.game_over:
            #print(self.player.items)
            try:
                self.control()
            except Task_Failure as a:
                self.inputbox.next(str(a))
                comands=[]
                self.pressed_key=None
            self.player.vision()
            self.sprites.clear(self.screen, self.background)
            dirty = self.sprites.draw(self.screen)
            self.sprites.update()
            self.overlays.draw(self.screen)
            pygame.display.update(dirty)
            dirty = self.overlays.draw(self.screen)
            pygame.display.update(dirty)
            self.clock.tick(15)
            if self.waiting:
                comands=self.recognize(self.inputbox.main())
                self.waiting=False
                #print(comands)
            if not self.player.action and len(comands)==0:
                self.waiting=True
            """for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    self.game_over = True
                elif event.type == pygame.locals.KEYDOWN and self.player.animation == None:
                    self.pressed_key = event.key"""
            if not self.player.action and len(comands)>0:
                comand=comands[0]
                comands=comands[1:]
                self.pressed_key=comand
if __name__=='__main__':
    game = Game()
    game.game_loop()