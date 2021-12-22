import sys
from collections import deque
import copy
import bisect
from collections import defaultdict
from itertools import combinations

#define directions as tuples
NORTH=(0,-1)
EAST=(1,0)
SOUTH=(0,1)
WEST=(-1,0)
DIRS=[NORTH,WEST,SOUTH,EAST]
#get right,ahead, and left directions from direction
def test_dirs(dir):
    rtidx = DIRS.index(dir)-1
    if rtidx<0:rtidx+=4
    return (DIRS*2)[rtidx:rtidx+3]

#vector ops on tuples to avoid complex and floating point
import operator
#component-wise addition
def add(a,b):
    return tuple(map(operator.add,a,b))
def subtract(a,b):
    return tuple(map(operator.sub,a,b))
def positivemod(pt,dim):
    return ((pt[0]%dim[0]+dim[0])%dim[0],(pt[1]%dim[1]+dim[1])%dim[1])
from math import dist

#reports snake collisions
class Collision(Exception):
    def __init__(self, point):
        self.point = point
        self.message = f"Snake collision at {point}"
        super().__init__(self.message)

#contains all program state
class Snak:
    
    class Snake:
        
        def __init__(self,x,y,dir,length):
            self.pos=(x,y)
            self.dir=dir
            self.length=length
            self.pts=deque([(x,y)])
            self.xpts=defaultdict(list)
            self.xpts[x].append(y)
            self.ypts=defaultdict(list)
            self.ypts[y].append(x)
            
        def changeLength(self,inc):
            self.length+=inc
            if len(self.pts)>self.length:
                self.removeLastPoint()
            if not self.length:
                raise IndexError("snake starved")
            
        #can snake see the target point? (is its head in the same row/column with no snake bodies in the way?)
        def canSee(self,target,snakes): #now runs O(lg n) in the number of points in the snake on the line we're examining
            #import pdb;pdb.set_trace()
            for snake in snakes:
                if target[0]!=self.pos[0]:
                    if len(snake.ypts[self.pos[1]])==1: #most common situation succeeds fast
                        return True
                    t = bisect.bisect_left(snake.ypts[self.pos[1]],target[0])
                    p = bisect.bisect_left(snake.ypts[self.pos[1]],self.pos[0])
                    if abs(t-p)>1 or snake!=self and abs(t-p)>0: #that is, if there is a point in the list between them
                        return False
                else:
                    if len(snake.xpts[self.pos[0]])==1: #most common situation succeeds fast
                        return True
                    t = bisect.bisect_left(snake.xpts[self.pos[0]],target[1])
                    p = bisect.bisect_left(snake.xpts[self.pos[0]],self.pos[1])
                    if abs(t-p)>1 or snake!=self and abs(t-p)>0: #that is, if there is a point in the list between them
                        return False
            return True
        
        #take a step in the current direction and return whether it succeeded
        def step(self):
            self.pos=add(self.pos,self.dir)
            if len(self.pts) >= self.length:
                self.removeLastPoint()
            if self.includesPt(self.pos):
                raise Collision(self.pos)
            self.pts.appendleft(self.pos)
            bisect.insort(self.xpts[self.pos[0]],self.pos[1]) #potential speedup: remember insertion point from inclusion check
            bisect.insort(self.ypts[self.pos[1]],self.pos[0])
            
        def reprAt(self,pos):
            if self.pos==pos:
                return '@'
            if self.includesPt(pos):
                return '#'
            return ''
            
        def includesPt(self,pt):
            i = bisect.bisect_left(self.xpts[pt[0]],pt[1])
            return i<len(self.xpts[pt[0]]) and self.xpts[pt[0]][i]==pt[1]
            
        def removeLastPoint(self):
            pt = self.pts.pop()
            #consider speeding these up if necessary
            self.xpts[pt[0]].remove(pt[1])
            self.ypts[pt[1]].remove(pt[0])
            
        def __len__(self):
            return self.length
    
    class Fruit:
        
        def __init__(self,x,y,type,immutable=False):
            self.pos=(x,y)
            self.type=type
            self.immutable=immutable
            #dict of relative coordinates of next fruit in each direction
            self.next=dict({NORTH:None,EAST:None,SOUTH:None,WEST:None})
        
        #get coordinates of next fruit in direction that isn't in deleted list, and update next as necessary
        def getNext(self,pos,dir,deleted):
            coord=add(pos,self.next[dir])
            if coord in deleted:
                coord=deleted[coord].getNext(coord,dir,deleted)
                if not self.immutable: self.next[dir]=subtract(coord,pos)
            return coord
        
        def __str__(self):
            return '+' if self.type>0 else '-'
    
    def __init__(self,lines,length):
        self.width = max(len(line.strip("\r\n")) for line in lines)
        self.height = len(lines)
        self.baseFruits = defaultdict(lambda:None)
        self.deletedFruits = dict()
        self.snakes = []
        self.selectedSnake=None;
        
        #set up fruits and snake
        for y,line in enumerate(lines):
            for x,c in enumerate(line):
                if c=='+' or c=='-':
                    self.baseFruits[(x,y)]=self.Fruit(x,y,int(c+'1'),True)
                if c in '^><v':
                    self.snakes.append(self.Snake(x,y,DIRS["^<v>".index(c)],length))
        
        #set up nearest fruit offset map
        self.nextFruit = dict()
        for x in range(self.width):
            for y in range(self.height):
                dirs = defaultdict(lambda:None)
                #if (x,y)==(33,1):import pdb;pdb.set_trace()
                northsouth=list(filter(lambda pos:pos[0]==x,self.baseFruits.keys()))
                if northsouth:
                    northidx=bisect.bisect_left(northsouth,(x,y))-1 #last coordinate less than this point
                    dirs[NORTH]=(0,northsouth[northidx][1]-y-(northidx<0)*self.height)
                    
                    southidx=bisect.bisect_right(northsouth,(x,y))
                    dirs[SOUTH]=(0,northsouth[southidx%len(northsouth)][1]-y+(southidx>=len(northsouth))*self.height)
                
                eastwest=list(filter(lambda pos:pos[1]==y,self.baseFruits.keys()))
                if eastwest:
                    eastidx=bisect.bisect_right(eastwest,(x,y))
                    dirs[EAST]=(eastwest[eastidx%len(eastwest)][0]-x+(eastidx>=len(eastwest))*self.width,0)
                    westidx=bisect.bisect_left(eastwest,(x,y))-1
                    dirs[WEST]=(eastwest[westidx][0]-x-(westidx<0)*self.width,0)
                self.nextFruit[(x,y)]=dirs
        
        #set up next fruit for base fruits
        for pos in self.baseFruits:
            for dir in DIRS:
                nextcell = positivemod(add(pos,dir),(self.width,self.height))
                self.baseFruits[pos].next[dir]=dir if nextcell in self.baseFruits else add(dir,self.nextFruit[nextcell][dir])
    
    #look up coordinates of next not-deleted fruit in the given direction
    def getNextFruit(self,pos,dir):
        basepos = positivemod(pos,(self.width,self.height))
        offset = self.nextFruit[basepos][dir]
        if offset is None:
            return
        target = add(pos,offset)
        if (target in self.deletedFruits):
            return self.deletedFruits[target].getNext(target,dir,self.deletedFruits)
        else:
            return target
        
    #delete fruit at position and update snake that ate it
    def consumeFruit(self,snake):
        basefruit = self.getFruit(snake.pos)
        if basefruit is None:
            return
        fruit = copy.copy(basefruit)
        fruit.immutable = False
        fruit.pos = snake.pos
        self.deletedFruits[snake.pos]=fruit
        snake.changeLength(fruit.type)
        
    #find the fruit at a given position, if any
    def getFruit(self,pos):
        if pos in self.deletedFruits:
            return
        basepos = positivemod(pos,(self.width,self.height))
        return self.baseFruits[basepos]
        
    #do one step of simulation
    def update(self):
        #first, advance all snakes (checks self-collision)
        for snake in self.snakes:
            snake.step()
            
        #check for collisions between different snakes
        for snake,othersnake in combinations(self.snakes,2):
            if othersnake.includesPt(snake.pos) or snake.includesPt(othersnake.pos):
                raise Collision(snake.pos)
        
        #alright, stepping succeeded! now eat any fruits that need eating and update snake directions!
        for snake in self.snakes:
            self.consumeFruit(snake)
            candidateFruits = list(filter(lambda x:type(x) is tuple and snake.canSee(x,self.snakes),[self.getNextFruit(snake.pos,dir) for dir in test_dirs(snake.dir)]))
            if candidateFruits:
                candidateDists = map(dist,candidateFruits,[snake.pos]*3)
                bestFruit = sorted(zip(candidateDists,range(3),candidateFruits))[0][2]
                snake.dir = tuple(map(lambda x:(x>0)-(x<0),subtract(bestFruit,snake.pos)))

            
    def reprAt(self,pos):
        pt=positivemod(pos,(self.width,self.height))
        output = ''.join(snake.reprAt(pos) for snake in self.snakes)
        if pos not in self.deletedFruits and self.baseFruits[pt] is not None:
            output+=str(self.baseFruits[pt])
        return (output+' ')[0]
        
    #get view coordinates that would center selected snake in view of given dimension
    def centeredView(self,width,height):
        if self.selectedSnake is not None:
            return subtract(self.snakes[self.selectedSnake].pos,(int(width/2),int(height/2)))
    
    #return whether a snake is selected
    def selectSnake(self,x,y):
        for i,snake in enumerate(self.snakes):
            if (x,y) in snake.pts:
                self.selectedSnake = i
                break
        else:
            self.selectedSnake = None
        return self.selectedSnake is not None
        
    def selectFirstSnake(self):
        self.selectedSnake = 0
        
    def selectNextSnake(self):
        if self.selectedSnake is not None:
            self.selectedSnake = (self.selectedSnake + 1)%len(self.snakes)
        
    def __str__(self):
        return "\n".join(f"Snake {i} final length: {snake.length}" for i,snake in enumerate(self.snakes))
    __repr__=__str__
                
def invisible(snak):
    try:
        while True:
            snak.update()
    except Collision:
        pass
    finally:
        print(str(snak))

def visible(stdscr,snak):
    import time
    viewy = (snak.height-stdscr.getmaxyx()[0])//2
    viewx = (snak.width-stdscr.getmaxyx()[1])//2
    pause = 0.5
    hold = True
    step = False
    stepcount = 1
    followSnake = False
    go=True
    key=-1
    
    #make color pairs
    curses.use_default_colors()
    curses.init_pair(0,-1,-1)
    curses.init_pair(1,curses.COLOR_GREEN,-1)
    curses.init_pair(2,curses.COLOR_RED,-1)
    curses.init_pair(3,curses.COLOR_YELLOW,-1)
    
    #map color pairs to chars
    colormap = {'#':1,'@':1,'+':2,'-':3,' ':0}
    
    #ask for mouse events
    stdscr.keypad(True)
    nomovemask = curses.BUTTON1_PRESSED|curses.BUTTON1_RELEASED|curses.BUTTON3_CLICKED
    movemask = nomovemask|curses.REPORT_MOUSE_POSITION
    availmask,_ = curses.mousemask(nomovemask)
    print("\033[?1003h\n")
    dragpt = None
    
    #helper functions for key updates
    def pauseupdate(multiplier):
        nonlocal pause,stepcount
        pause *= multiplier
        stepcount = 1
    
    def viewupdate(xadd,yadd):
        nonlocal viewx,viewy,followSnake
        followSnake = False
        viewy += yadd
        viewx += xadd
        
    def pauseunpause():
        nonlocal hold,stepcount,pause,step
        hold = not hold
        step = True
        stepcount+=pause
    
    def singlestep():
        nonlocal stepcount,pause,step
        step = True
        stepcount+=pause
        
    def followfirst():
        nonlocal snak,followSnake
        snak.selectFirstSnake()
        followSnake = True
        
    def stop():
        nonlocal go
        go = False
        
    #map keys to functions
    keymap = defaultdict(lambda:lambda:None,{
        ord('+'):lambda:pauseupdate(0.5),
        ord('-'):lambda:pauseupdate(2),
        ord('p'):pauseunpause,
        ord('s'):singlestep,
        ord('q'):stop,
        ord('n'):snak.selectNextSnake,
        ord('f'):followfirst,
        curses.KEY_UP:lambda:viewupdate(0,-8),
        curses.KEY_DOWN:lambda:viewupdate(0,8),
        curses.KEY_RIGHT:lambda:viewupdate(10,0),
        curses.KEY_LEFT:lambda:viewupdate(-10,0)
        })
    
    while go:
        if stepcount>=pause:
            #update sim
            if dragpt is None and (step or not hold): 
                while stepcount>0.5:
                    snak.update()
                    stepcount-=min(stepcount,1/max(1,1-math.frexp(5*pause)[1]))
                    if step: break
            step=False
            
            #render view into sim that fills the terminal
            stdscr.erase()
            if followSnake:
                viewx,viewy = snak.centeredView(stdscr.getmaxyx()[1],stdscr.getmaxyx()[0])
            for y in range(viewy,viewy+stdscr.getmaxyx()[0]):
                for x in range(viewx,viewx+stdscr.getmaxyx()[1]):
                    char = snak.reprAt((x,y))
                    try:
                        stdscr.addch(y-viewy,x-viewx,char,curses.color_pair(colormap[char]))
                    except curses.error:
                        pass
                    
            #redraw screen
            #stdscr.refresh()
            stepcount %= pause
        
        stepcount += 1
            
        #remember when we started
        then = time.perf_counter()
        waittime = int(1000*min(pause,0.5))
        while True:
            if hold:stdscr.timeout(-1)
            else:stdscr.timeout(waittime)
            #get key and wait
            key=stdscr.getch()
            
            #handle mouse
            if availmask and key==curses.KEY_MOUSE:
                try:
                    _,x,y,_,t = curses.getmouse()
                    curses.flushinp()
                    #print("mouse",x,y,t,file=sys.stderr)
                    if t & curses.BUTTON3_CLICKED:
                        #print("snake followed",file=sys.stderr)
                        followSnake = snak.selectSnake(x+viewx,y+viewy)
                        dragpt = None
                    elif t & curses.BUTTON1_PRESSED:
                        dragpt = (x,y)
                        hold = True
                        curses.mousemask(movemask)
                    elif t & curses.BUTTON1_RELEASED and dragpt is not None:
                        dragpt = None
                        hold = False
                        curses.mousemask(nomovemask)
                    elif t & curses.REPORT_MOUSE_POSITION and dragpt is not None and dragpt!=(x,y):
                        followSnake = False
                        viewx -= x-dragpt[0]
                        viewy -= y-dragpt[1]
                        dragpt = (x,y)
                except curses.error as e:
                    #i have no idea what triggers some mouse movement errors
                    #but we don't need to register them.
                    #just try again
                    #print("mouse error",file=sys.stderr)
                    waittime -= int(1000*(time.perf_counter()-then))
                    if waittime>=0:
                        continue
            else:
                #do what the key does
                keymap[key]()
            
            break
    

if __name__=="__main__":
    
    #parse command line args
    import argparse
    parser = argparse.ArgumentParser(description='Run and visualize a Snak program.')
    parser.add_argument('source_file', metavar='filename',
                    help='path to Snak program file')
    parser.add_argument('length', metavar='length', type=int, help='Initial length of snake')
    parser.add_argument('-q', '--quiet', action='store_false', help='Flag to run program without visualization')
    parser.add_argument('-t', '--timeout', type=int, default=0, help='Automatically kill after this many seconds in quiet mode')
    args=parser.parse_args()
    visualize = args.quiet
    
    #read in program
    with open(args.source_file) as f:
        snak = Snak(f.readlines(),args.length)
    
    #run program
    if visualize:
        #start app with initialized terminal
        import curses
        import math
        import time
        try:
            curses.wrapper(visible,snak)
        except Collision: #collisions are the intended way to halt and should not error
            pass
        finally:
            print(snak)
    else:
        if args.timeout:
            import signal
            def handler(signum,frame):
                sys.exit()
            signal.signal(signal.SIGALRM,handler)
            signal.alarm(args.timeout)
            invisible(snak)
            signal.alarm(0)
        else:
            invisible(snak)
        