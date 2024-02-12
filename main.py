import grids
import tkinter as tk
import random

class Battleship(tk.Frame):
    def __init__(self, our_grid, their_grid):
        root = tk.Tk()
        super().__init__(root)
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        self.pack()
        self.our_grid = our_grid
        self.their_grid = their_grid
        
        # DIFFICULTY
        l = input('Please choose the difficulty level (1-5): ')
        while not l.isnumeric() or int(l) < 1 or int(l) > 5:
            l = input('Please choose the difficulty level (1-5): ')
        strategies = {1:level_1, 2:level_2, 3:level_3, 4:level_4, 5:level_5}
        self.strategy = strategies[int(l)]

        # VISUALIZE
        h = max(our_grid.y, their_grid.y)
        if h < 13:
            self.scale = 30
        elif h < 15:
            self.scale = 25
        elif h < 19:
            self.scale = 20
        else:
            self.scale = 17
            
        # DISPLAY OUR GRID (ships visible)
        self.our_canvas = tk.Canvas(self, bg ='white',
                                    width = self.our_grid.x*self.scale, height = self.our_grid.y*self.scale)
        self.our_canvas.pack()        
        for x in range(1, self.our_grid.x):
            self.our_canvas.create_line(x*self.scale, 0, 
                                        x*self.scale, self.our_grid.y*self.scale,
                                        fill = '#D3D3D3')
        for y in range(1, self.our_grid.y):
            self.our_canvas.create_line(0, y*self.scale,
                                        self.our_grid.x*self.scale, y*self.scale,
                                        fill = '#D3D3D3')
        for ship in self.our_grid.ships:
            for x, y in ship.pos:
                self.our_canvas.create_rectangle(x*self.scale, y*self.scale,
                                                 (x + 1)*self.scale - 1, (y + 1)*self.scale - 1,
                                                 fill= 'red', outline='#D3D3D3')

        # SPACE BETWEEN
        self.canvasmiddle = tk.Canvas(self, width = self.scale, height = self.scale)
        self.canvasmiddle.pack()

        # DISPLAY THEIR GRID (ships not visible)
        self.their_canvas = tk.Canvas(self, bg ='white',
                                      width = self.their_grid.x*self.scale, height = self.their_grid.y*self.scale)
        self.their_canvas.bind("<Button-1>", self.shoot)
        self.their_canvas.pack()
        for x in range(1, self.their_grid.x):
            self.their_canvas.create_line(x*self.scale, 0, 
                                          x*self.scale, self.their_grid.y*self.scale,
                                          fill = '#D3D3D3')
        for y in range(1, self.their_grid.y):
            self.their_canvas.create_line(0, y*self.scale,
                                          self.their_grid.x*self.scale, y*self.scale,
                                          fill = '#D3D3D3')
        

    def shoot(self, target):
        # OUR SHOT
        x, y = target.x//self.scale, target.y//self.scale
        shot_before = any((x,y) in s.pos for s in self.their_grid.ships)
        res, ship = self.their_grid.shoot((x, y))
        if res == 0 and not shot_before: # miss
            self.their_canvas.create_oval(x*self.scale + 1, y * self.scale + 1,
                                          (x + 1)*self.scale - 1, (y + 1)*self.scale - 1,
                                          fill = 'blue')
        elif res != 0: # hit
            self.their_canvas.create_oval(x*self.scale + 1, y*self.scale + 1,
                                          (x + 1)*self.scale - 1, (y + 1)*self.scale - 1,
                                          fill = 'red')
        if ship is not None: # sink ship
            for x, y in ship.pos:
                self.their_canvas.create_rectangle(x*self.scale, y*self.scale,
                                                   (x + 1)*self.scale - 1, (y + 1)*self.scale - 1,
                                                   fill = 'red', outline = '#D3D3D3')

        # THEIR SHOT
        hidden = grids.HiddenGrid(self.our_grid)
        x, y = self.strategy(hidden)
        res, ship = self.our_grid.shoot((x, y))
        if res == 0: # miss
            self.our_canvas.create_oval(x*self.scale + 1, y*self.scale + 1,
                                        (x + 1)*self.scale - 1, (y + 1)*self.scale - 1,
                                        fill= 'blue')
        else: # hit
            self.our_canvas.create_oval(x*self.scale + 1, y*self.scale + 1,
                                        (x + 1)*self.scale - 1, (y + 1)*self.scale - 1,
                                        fill = 'yellow')
            
        # CHECK GAME OVER
        our_alive = set([s.is_afloat() for s in self.our_grid.ships])
        their_alive = set([s.is_afloat() for s in self.their_grid.ships])
        if their_alive == {False}:
            print('GAME OVER\nYOU WIN')
        elif our_alive == {False}:
            print('GAME OVER\nYOU LOSE')

# LEVELS
def level_1(hidden_grid):
    """
    Takes completely random shots
    """
    return (random.randint(0, hidden_grid.x - 1), random.randint(0, hidden_grid.y - 1))

def level_2(hidden_grid):
    """
    Takes random shots but does not shoot the same spot twice
    """
    while True: # will break when proper position is found
        pos = (random.randint(0, hidden_grid.x - 1), random.randint(0, hidden_grid.y - 1))
        if pos not in hidden_grid.hits and pos not in hidden_grid.misses:
            return pos

def level_3(hidden_grid):
    """
    Tries to sink a ship once it's been hit by hitting all around the hit point
    """
    sunk_hits = set() # all these hits already sunk a ship
    for s in hidden_grid.sunken_ships:
        sunk_hits.update(s.pos)
        
    for h in hidden_grid.hits:
        if h not in sunk_hits:
            poss_opts = [(h[0] - 1, h[1]), (h[0] + 1, h[1]), (h[0], h[1] - 1), (h[0], h[1] + 1)]
            real_opts = []
            while poss_opts:
                o = poss_opts.pop()
                if (0 <= o[0] < hidden_grid.x and
                    0 <= o[1] < hidden_grid.y and
                    o not in hidden_grid.hits and
                    o not in hidden_grid.misses):
                    # in grid and not attempted prior
                    real_opts.append(o)
                    
            if not len(real_opts) == 0: # there are available options, continue to next hit otherwise
                return real_opts[random.randint(0, len(real_opts) - 1)]
            
    # no smarter options found
    return level_2(hidden_grid)

def level_4(hidden_grid):
    """
    Tries to sink a ship once it's been hit by hitting all around the hit point
    If another hit is successful, contunues of the same line (vert, hor) to
    sink the ship faster
    """
    sunk_hits = set() # all these hits already sunk a ship
    for s in hidden_grid.sunken_ships:
        sunk_hits.update(s.pos)
        
    for h in hidden_grid.hits:
        if h not in sunk_hits:
            poss_opts = [(h[0] - 1, h[1]), (h[0] + 1, h[1]), (h[0], h[1] - 1), (h[0], h[1] + 1)]
            real_opts = []
            
            while poss_opts:
                o = poss_opts.pop()
                if (0 <= o[0] < hidden_grid.x and
                    0 <= o[1] < hidden_grid.y and
                    o not in hidden_grid.hits and
                    o not in hidden_grid.misses):
                    # in grid and not attempted prior
                    real_opts.append(o)
                    
            if not len(real_opts) == 0: # there are available options, continue to next hit otherwise
                for o in real_opts: # in case multiple spots in a ship are hit
                    if ((o[0] - 2, o[1]) in hidden_grid.hits and
                        (o[0] - 2, o[1]) not in sunk_hits and
                        0 <= o[0] - 2 < hidden_grid.x or
                        (o[0] + 2, o[1]) in hidden_grid.hits and
                        (o[0] + 2, o[1]) not in sunk_hits and
                        0 <= o[0] + 2 < hidden_grid.x or
                        (o[0], o[1] - 2) in hidden_grid.hits and
                        (o[0], o[1] - 2) not in sunk_hits and
                        0 <= o[1] - 2 < hidden_grid.y or
                        (o[0], o[1] + 2) in hidden_grid.hits and
                        (o[0], o[1] + 2) not in sunk_hits and
                        0 <= o[1] + 2 < hidden_grid.y):
                        return o
                return real_opts[random.randint(0, len(real_opts) - 1)]
            
    # no smarter options found
    return level_2(hidden_grid)

def level_5(hidden_grid):
    """
    Tries to sink a ship once it's been hit by hitting all around the hit point
    If another hit is successful, contunues of the same line (vert, hor) to
    sink the ship faster
    If there is an unshot spot directly between two shots, tries to shoot there
    """
    sunk_hits = set() # all these hits already sunk a ship
    for s in hidden_grid.sunken_ships:
        sunk_hits.update(s.pos)
        
    for h in hidden_grid.hits:
        if h not in sunk_hits:
            poss_opts = [(h[0] - 1, h[1]), (h[0] + 1, h[1]), (h[0], h[1] - 1), (h[0], h[1] + 1)]
            real_opts = []
            
            while poss_opts:
                o = poss_opts.pop()
                if (0 <= o[0] < hidden_grid.x and
                    0 <= o[1] < hidden_grid.y and
                    o not in hidden_grid.hits and
                    o not in hidden_grid.misses):
                    # in grid and not attempted prior
                    real_opts.append(o)
                    
            if not len(real_opts) == 0: # there are available options, continue to next hit otherwise
                for o in real_opts: # in case multiple spots in a ship are hit
                    if ((o[0] - 2, o[1]) in hidden_grid.hits and
                        (o[0] - 2, o[1]) not in sunk_hits and
                        0 <= o[0] - 2 < hidden_grid.x or
                        (o[0] + 2, o[1]) in hidden_grid.hits and
                        (o[0] + 2, o[1]) not in sunk_hits and
                        0 <= o[0] + 2 < hidden_grid.x or
                        (o[0], o[1] - 2) in hidden_grid.hits and
                        (o[0], o[1] - 2) not in sunk_hits and
                        0 <= o[1] - 2 < hidden_grid.y or
                        (o[0], o[1] + 2) in hidden_grid.hits and
                        (o[0], o[1] + 2) not in sunk_hits and
                        0 <= o[1] + 2 < hidden_grid.y or
                        (o[0] - 3, o[1]) in hidden_grid.hits and
                        (o[0] - 3, o[1]) not in sunk_hits and
                        0 <= o[0] - 3 < hidden_grid.x or
                        (o[0] + 3, o[1]) in hidden_grid.hits and
                        (o[0] + 3, o[1]) not in sunk_hits and
                        0 <= o[0] + 3 < hidden_grid.x or
                        (o[0], o[1] - 3) in hidden_grid.hits and
                        (o[0], o[1] - 3) not in sunk_hits and
                        0 <= o[1] - 3 < hidden_grid.y or
                        (o[0], o[1] + 3) in hidden_grid.hits and
                        (o[0], o[1] + 3) not in sunk_hits and
                        0 <= o[1] + 3 < hidden_grid.y):
                        return o
                return real_opts[random.randint(0, len(real_opts) - 1)]
            
    # no smarter options found
    return level_2(hidden_grid)

# START GAME

print('Welcome to the game of battleship!\n\nTo start, please select the grid width and height (10-20):')
w = input('width: ')
while not w.isnumeric() or int(w) < 10 or int(w) > 20:
    w = input('width: ')
h = input('height: ')
while not h.isnumeric() or int(h) < 10 or int(h) > 20:
    h = input('height: ')
    
g1 = grids.Grid(int(w), int(h))
g2 = grids.Grid(int(w), int(h))

n = input('How many ships should there be (5-15): ')
while not n.isnumeric() or int(n) < 5 or int(n) > 15:
    n = input('How many ships should there be (5-15): ')
    
g1.create_random(int(n))
g2.create_random(int(n))

print('\nAmazing! Time to start the game\n')

Battleship(g1, g2).mainloop()