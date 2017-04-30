import numpy as np



class lens:

    d = 0
    r1 = 0
    r2 = 0
    matrix = []
    x = 0
    y = 200
    n = 1.5
    color = '#0066ff'
    f = 0
    t = 0
    thin_lens = True

    def __init__(self, diameter, rad1, rad2, x, n=1.5, t=0.):
        self.d = diameter
        self.r1 = rad1
        self.r2 = rad2
        self.x = x
        self.n = n
        self.t = t
        self.thin_lens = False
        if t <= 0:
            self.thin_lens = True
        if self.thin_lens:
            self.f = self.focalpt(n, rad1, rad2)
            self.matrix = self.tmthinlens(self.f)
        if not self.thin_lens:
            self.matrix = self.thicklens(1.0, n, rad1, rad2, t)
            self.f = 10.

    def __str__ (self):
        return str(self.matrix)

    def draw(self,canvas):  # draws the lens parametrically using its diameter, x-coord, and radii of curvature
        h = 2.*self.y
        xpos = self.x
        r1 = self.r1
        r2 = self.r2
        k = float(self.t+10)
        ylim = self.d

        if r1 > 4582:
            r1 = 4582

        if r1 < -4582:
            r1 = -4582

        if r2 > 4582:
            r2 = 4582

        if r2 < -4582:
            r2 = -4582

        points1 = []
        points3x = []
        points3y = []
        points2 = []
        points3 = []
        points2x = []
        points2y = []
        points4 = []

        for t in range(0, 180):
            x = -1 * r1 * np.cos(t * np.pi / 360.) + r1 - k + xpos
            y = -1 * np.abs(r1) * np.sin(t * np.pi / 360.) + h / 2.
            if y >= (h / 2. - ylim):
                points1.append(x)
                points1.append(y)
            else:
                break

        for t in range(0, 180):
            x = r2 * np.cos(t * np.pi / 360.) - r2 + k + xpos
            y = -1 * np.abs(r2) * np.sin(t * np.pi / 360.) + h / 2.
            if y >= (h / 2. - ylim):
                points2x.append(x)
                points2y.append(y)
            else:
                break

        for t in range(0, 180):
            x = -1 * r1 * np.cos(t * np.pi / 360.) + r1 - k + xpos
            y = np.abs(r1) * np.sin(t * np.pi / 360.) + h / 2.
            if y <= (h / 2. + ylim):
                points3x.append(x)
                points3y.append(y)
            else:
                break

        for t in range(0, 180):
            x = r2 * np.cos(t * np.pi / 360.) - r2 + k + xpos
            y = np.abs(r2) * np.sin(t * np.pi / 360.) + h / 2.
            if y <= (h / 2. + ylim):
                points4.append(x)
                points4.append(y)
            else:
                break

        points2x.reverse()
        points2y.reverse()
        points3x.reverse()
        points3y.reverse()
        for i in range(len(points2x)):
            points2.append(points2x[i])
            points2.append(points2y[i])

        for i in range(len(points3x)):
            points3.append(points3x[i])
            points3.append(points3y[i])
        points = points1, points2, points4, points3
        canvas.create_polygon(points, fill=self.color)
        canvas.pack()
        self.x = xpos
        return

    """Function that generates transformation matrix for a thin lens, given the focal point"""

    def tmthinlens(self,f):
        thin = np.matrix([[1, 0], [(-1. / f), 1]])
        return thin

    """Function that finds the focal point for a thin lens using the lens maker formula
        takes indices of refraction, radii of curvature"""

    def focalpt(self, nL, r1, r2, nOut=1):
        r1 = float(r1)
        r2 = -1*float(r2)
        nL = float(nL)
        if r1-r2 == 0:
            return np.inf
        P = (nL - nOut) / nOut * (1 / r1 - 1 / r2)

        return 1 / P

    """Function that generates transformation matrix for refraction at a flat boundary, given 2 indices of refraction"""

    def refraction(self,n1, n2):
        n1 = float(n1)
        n2 = float(n2)
        n = n1 / n2
        rf = np.matrix([[1, 0], [0, n]])
        return rf

    """Function that generates transformation matrix for refraction at a curved boundary, given 2 indices of refraction and radius of curvature"""

    def c_refraction(self,n1, n2, r):
        n1 = float(n1)
        n2 = float(n2)
        r = float(r)
        n = n1 / n2
        a = (n1 - n2) / (r * n2)
        rf = np.matrix([[1, 0], [a, n]])
        return rf

    """Function that generates transformation matrix for a thick lens, given center thickness of thick lens, radii of curvature, and indices of refraction"""

    def thicklens(self, n1, n2, r1, r2, s):
        thick1 = self.c_refraction(n2, n1, str(-1*float(r2)))
        thick2 = np.matrix([[1, float(s)], [0, 1]])
        thick3 = self.c_refraction(n1, n2, r1)
        thick = np.dot(np.dot(thick1, thick2), thick3)
        return thick