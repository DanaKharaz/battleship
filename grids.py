import random

class Ship:
    """
    A ship that can be placed on the grid.
    """
    def __init__(self, pos):
        self.pos = pos
        self.hits = set()
    def __repr__(self):
        return f"Ship('{self.name}', {self.pos})"

    def __str__(self):
        return f'{repr(self)} with hits {self.hits}'
    
    def __eq__(self, other):
        return (self.pos == other.pos and
                self.hits == other.hits)
    
    def is_afloat(self):
        return not self.pos == self.hits
    
    def take_shot(self, shot):
        if not shot in self.pos or shot in self.hits:
            return 0 # miss
        self.hits.add(shot) # definately hit otherwise
        if self.is_afloat():
            return 1 # hit
        return 2 # destroyed
        
class Grid:
    """
    The grid on which the Ships are placed.
    Remembers the shots fired that missed all of the Ships (combined)
    """    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ships = []
        self.misses = set()
    
    def add_ship(self, ship):
        """
        Add a Ship to the grid avoiding collisions with other ships
        """
        for s in self.ships:
            for p in ship.pos:
                if p in s.pos:
                    return
        self.ships.append(ship)
    
    def shoot(self, shot):
        for s in self.ships:
            res = s.take_shot(shot)
            if res == 2:
                return (2, s)
            if res == 1:
                return (1, None)
        self.misses.add(shot)
        return (0, None)
    
    def random_ship(self):
        taken = set()
        for s in self.ships:
            taken.update(s.pos)
            
        while True: # will break when proper ship is found
            i = random.randint(0, 8)
            ship_length = [6, 5, 4, 4, 3, 3, 3, 2, 2][i]
            if random.randint(0, 1) == 0: # horizontal
                y = random.randint(0, self.y - 1)
                x = random.randint(0, self.x - ship_length - 1)
                pos = set([(x + i, y) for i in range(ship_length)])
                if pos.isdisjoint(taken):
                    return Ship(pos)
            else: # vertical
                x = random.randint(0, self.x - 1)
                y = random.randint(0, self.y - ship_length - 1)
                pos = set([(x, y + i) for i in range(ship_length)])
                if pos.isdisjoint(taken):
                    return Ship(pos)
    
    def create_random(self, n):
        for i in range(n):
            self.add_ship(self.random_ship())

class HiddenGrid:
    """
    Hides our ships from the opponent's view of the grid.
    """
    def __init__(self, grid):
        self.x = grid.x
        self.y = grid.y
        self.misses = grid.misses
        self.hits = set()
        self.sunken_ships = []
        for s in grid.ships:
            self.hits.update(s.hits)
            if not s.is_afloat():
                self.sunken_ships.append(s)