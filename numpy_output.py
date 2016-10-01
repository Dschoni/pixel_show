import numpy as np
import time



class game(object):
    def __init__(self,size,device = '/dev/spidev0.0'):
        self.field = np.zeros((size,size,3),dtype=np.uint8)
        self.snake = [[1,0],[1,1],[1,2]]
        self.apple = [0,5]
        self.o = open(device,'w')
        self.direction = 'u'
        self.delay=0.5
        self.alive = True
    def run(self):
        t1 = time.clock()
        while self.alive:
            time.sleep(self.delay)
            self.m()
            self.u()
            
    def output_array(self,arr):
        for i in range(arr.shape[0]):
            if i%2==1:
                arr[i]=arr[i][::-1]
        self.o.write(arr.tostring())
        self.o.flush()
    def u(self):
        game = self.field.copy()
        for i in range(len(self.snake)):
            try:
                x,y=self.snake[i]
                game[x,y]=[0,255,0]
            except IndexError:
                self.alive = False
        x,y = self.apple
        game[x,y]=[255,0,0]
        if self.alive:
            self.output_array(game)
    def m(self):
        head = self.snake[-1]
        if self.direction == 'u':
            self.snake.append([head[0],head[1]+1])
            self.snake = self.snake[1:]
        elif self.direction == 'l':
            self.snake.append([head[0]+1,head[1]])
            self.snake = self.snake[1:]
        elif self.direction == 'd':
            self.snake.append([head[0],head[1]-1])
            self.snake = self.snake[1:]
        elif self.direction == 'r':
            self.snake = self.snake.append([head[0]-1,head[1]])
            self.snake = self.snake[1:]
    def hit(self):
        if self.apple in self.snake:
            self.apple_move()
delay = 1
dev = '/dev/spidev0.0'
o = open(dev,'w')
x = 10
y = 10
output = np.zeros((x,y,3),dtype=np.uint8)
blank = output.copy()
red = output.copy()
red[:,:,0]=255
blue = output.copy()
blue[:,:,2]=255
green = output.copy()
green[:,:,1]=255
test = output.copy()
#game = output.copy()
output[1,1]=[255,255,255]
test[:4,:3,0]=255
def c():
    o.write(blank.tostring())
    o.flush()
def d():
    o.write(output.tostring())
    o.flush()
def crazy():
    r = red
    g = green
    b = blue
    while True:
        output_array(r)
        time.sleep(delay)
        output_array(g)
        time.sleep(delay)
        output_array(b)
        time.sleep(delay)
def output_array(arr):
    for i in range(arr.shape[0]):
        if i%2==1:
            arr[i]=arr[i][::-1]
    o.write(arr.tostring())
    o.flush()

s = game(10)
s.run()

