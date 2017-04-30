import numpy as np

# class obj handels how objects in the simulation act
# includes a height, x-coordinate, and angles of emitted rays as properties
class obj:

    h = 0
    x = 0
    theta = [-.02, -.04,0.0,.02,.04]
    #theta = [0.0] #Add different start angles here!
    y = 200

    def __init__(self, h, x):
        self.h = h
        self.x = x

    def __str__(self):
        return str(np.array([self.h, self.x]))

    def draw(self, canvas):  # draws itself as a rectangle
        canvas.create_rectangle(self.x + 2, self.y, self.x - 2, self.y - self.h, fill='black')
        canvas.pack()
