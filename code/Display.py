try:
	from tkinter import *
except Exception:
	pass
try:
	from Tkinter import *
except Exception:
	pass
from Lens import lens
import numpy as np
from Object import obj


class Display:
    w = 1600  # window width
    h = 400  # window height
    Lenses = []  # keeps track of on screen lenses
    canv = []   # references the canvas objects are drawn upon
    ob = []  # keeps track of ray producing objects
    selectO = []   # keeps track of clicked on object
    selectL = []  # keeps track of click on lens
    selectWindow = 0  # keeps track of secondary info window

    def __init__(self, master):  # initializes the display class

        canvas = Canvas(master, width=self.w, height=self.h)  # the canvas everything is drawn on
        canvas.pack()
        self.initialize(canvas)

        frame = Frame(master)  # a place to put labels and entry fields
        frame.pack()  # packs the frame to the master window

        canvas.bind("<Button-1>",self.left_click)  # binds the left click to an action
        canvas.bind("<Button-3>", self.right_click)  # binds the right click to an action
        canvas.bind("<B1-Motion>", self.left_drag)  # binds the left drag to an action

        self.button = Button(  # creates a quit button that ends the program
            frame, text="QUIT", fg="red", command=frame.quit
        )
        self.button.pack(side=LEFT)

        self.xframe = Frame(master)  # creates an entry widget that guides item x-axis position
        self.xpos = Entry(self.xframe)
        self.xpos.insert(0, "420")
        self.xpos.pack(side=RIGHT)
        self.xL = Label(self.xframe, text='Axial Position')
        self.xL.pack(side=LEFT)

        self.dframe = Frame(master)  # creates an entry widget that guides item y-axis height
        self.diameter = Entry(self.dframe)
        self.diameter.insert(0, "80")
        self.diameter.pack(side=RIGHT)
        self.dL = Label(self.dframe, text='Vertical Diameter')
        self.dL.pack(side=LEFT)

        self.r1frame = Frame(master)  # creates an entry widget that guides lens right radius value
        self.r1 = Entry(self.r1frame)
        self.r1.insert(0, "300")
        self.r1.pack(side=RIGHT)
        self.r1L = Label(self.r1frame, text='Left Radius of Curvature')
        self.r1L.pack(side=LEFT)

        self.r2frame = Frame(master)  # creates an entry widget that guides lens left radius value
        self.r2 = Entry(self.r2frame)
        self.r2.insert(0, "300")
        self.r2.pack(side=RIGHT)
        self.r2L = Label(self.r2frame, text='Right Radius of Curvature')
        self.r2L.pack(side=LEFT)

        self.nframe = Frame(master)  # creates an entry widget that guides lens index of refraction value
        self.n = Entry(self.nframe)
        self.n.insert(0, "1.5")
        self.n.pack(side=RIGHT)
        self.nL = Label(self.nframe, text='Index of Refraction')
        self.nL.pack(side=LEFT)

        self.tframe = Frame(master)  # creates an entry widget that guides lens thickness value
        self.t = Entry(self.tframe)
        self.t.insert(0, '0')
        self.t.pack(side=RIGHT)
        self.tL = Label(self.tframe, text='Thickness')
        self.tL.pack(side=LEFT)

        self.dframe.pack(side=BOTTOM)  # packs entry/labels pairs into main window
        self.r1frame.pack(side=TOP)
        self.r2frame.pack(side=TOP)
        self.xframe.pack(side=BOTTOM)
        self.nframe.pack(side=BOTTOM)
        self.tframe.pack(side=BOTTOM)
        entries = [self.diameter, self.r1, self.r2, self.xpos, self.n, self.t]  # simplified list of gathered properties

        self.button = Button(  # creates a button that adds an object to the simulation
            frame, text="Add Object", fg="black",  # obj height and x coordinate are taken from the entry widgets
            command=lambda: self.draw_object(canvas, int(self.diameter.get()), int(self.xpos.get()))
        )
        self.button.pack(side=RIGHT)

        self.button = Button(  # creates a button that generates rays from placed objects i.e. runs simulation
            frame, text="Generate Rays", fg="dark green",
            command=lambda: self.generate_ray(canvas)
        )
        self.button.pack(side=RIGHT)

        self.create = Button(  # creates a button that adds a lens to the simulation
            frame, text="Add Lens", fg="dark blue",
            command=lambda: self.draw_lens(canvas, entries))
        self.create.pack(side=RIGHT)  # properties are taken from the entry widgets

        self.clear = Button(  # creates a button that clears all optical elements from canvas
            frame, text="CLEAR", fg="dark red", command=lambda: self.clear_all(canvas))
        self.clear.pack(side=BOTTOM)
        self.canv = canvas

    def initialize(self, canvas):  # draws the optical axis
        canvas.create_line(0, self.h / 2., self.w, self.h / 2., fill="red", dash=(4, 4))

    def draw_object(self, canvas, new_height, x):  # adds an object to the simulation with height h and x-coord x
        new_object = obj(new_height, x)
        self.ob.append(new_object)
        new_object.draw(canvas)

    def draw_lens(self, canvas, entries):  # adds a lens to the simulation with below properties

        new_lens = lens(int(entries[0].get()), int(entries[1].get()), int(entries[2].get()), int(entries[3].get()),
                 float(entries[4].get()),float(entries[5].get()))
        self.Lenses.append(new_lens)
        new_lens.draw(canvas)

    def sortme(self):  # sorts the lenses by their x-coordinate
        self.Lenses.sort(key=lambda y: y.x, reverse=False)

    # intersect is a function that finds intersection of two lines from two points on each line
    def intersect(self,pts):
        if pts[1][0] - pts[0][0] < 0.00001 or pts[3][0] - pts[2][0] < 0.00001:
            return()
        slope1 = float(pts[1][1] - pts[0][1]) / (pts[1][0] - pts[0][0])
        slope2 = float(pts[3][1] - pts[2][1]) / (pts[3][0] - pts[2][0])
        b1 = pts[0][1] - slope1 * pts[0][0]
        b2 = pts[2][1] - slope2 * pts[2][0]
        if slope2 - slope1 < 0.0000001 and b1 - b2 > 0.00001:
            return ()
        if slope2-slope1 == 0.0:
            return()
        xintersect = float(b2 - b1) / (slope1 - slope2)
        yintersect = slope1 * xintersect + b1
        return (xintersect, yintersect)

    def generate_ray(self, canvas):  # generates the rays based on object and lens position and properties
        matrices = []
        if len(self.ob) == 0:  # ends it if there are no objects to generate rays
            return
        for O in self.ob:  # this is so that multiple objects are supported
            xpos = [O.x]  # this list keeps track of the position of all the optical elements
            ypos = [self.h]  # this list keeps track of the heights of all optical elements
            if len(self.Lenses) > 0:
                self.sortme()
                count = 0
                for le in self.Lenses:
                    xpos.append(le.x)
                    ypos.append(le.d)
                    xpos.append(le.x)
                    ypos.append(self.h)

                    matrices.append(self.drift(xpos[count], xpos[count + 1]))
                    matrices.append(le.matrix)

                    count += 2

                xpos.append(self.Lenses[len(self.Lenses) - 1].x + 1600)
                ypos.append(self.h)
                matrices.append(self.drift(xpos[len(self.Lenses)], xpos[len(self.Lenses)]+1600))
            else:
                xpos.append(xpos[0] + 1600)
                ypos.append(self.h)
                matrices.append(self.drift(xpos[0], xpos[1]))

            thetas = O.theta
            heights = [O.h] * len(thetas)

            for i in range(len(xpos)-1):  # this goes through each optical element and finds the new x,y coordinates
                                            # of the ray at each element and draws a line between the two
                tempThetas = []
                tempHeights = []
                pts = []
                for t in range(len(thetas)): # this supports multiple rays from one object
                    x1 = float(xpos[i])

                    x2 = float(xpos[i + 1])

                    v1 = np.array([heights[t], thetas[t]])
                    if np.abs(ypos[i]) > np.abs(heights[t]):
                        v2 = np.dot(matrices[i], v1)
                    else:
                        v2 = np.dot(np.matrix([[1., 0.], [0., 1.]]), v1)
                    tempHeights.append(v2[0, 0])
                    tempThetas.append(v2[0, 1])

                    pt1 = (x1, self.h / 2. - heights[t])
                    pt2 = (x2, self.h / 2. - v2[0, 0])

                    pts.append(pt1)
                    pts.append(pt2)
                    canvas.create_line(pt1[0], pt1[1], pt2[0], pt2[1])
                    if (t+6) % 2 == 1:
                        if len(self.intersect(pts)) > 0:  # this block detects intersections and draws images there
                            xposimage = self.intersect(pts)[0]
                            imageheight = self.intersect(pts)[1]
                            if np.abs(xposimage - O.x) > 0.0001 and matrices[i-1][1,0] < 0:
                                if pt2[0] > xposimage > pt1[0]:
                                    self.canv.create_rectangle(xposimage + 2, self.h / 2., xposimage - 2, imageheight,
                                                               fill='grey')
                            if np.abs(xposimage - O.x) > 0.0001 and matrices[i - 1][1, 0] > 0:
                                if xposimage < pt1[0]:
                                    self.canv.create_rectangle(xposimage + 2, self.h / 2., xposimage - 2, imageheight,
                                                               fill='grey')
                        pts = []
                thetas = tempThetas
                heights = tempHeights
            matrices = []
            canvas.pack()

    def drift(self, x1, x2):  # generates a matrix that representes linear drift between two optical elements
        d = x2 - x1
        dm = np.matrix([[1, d], [0, 1]])
        return dm

    def clear_all(self, canvas):  # clears all optical elements from field
        canvas.delete(ALL)
        self.Lenses = []
        self.ob = []
        self.initialize(canvas)

    def left_click(self,event):  # creates an info panel if an optical element is clicked
        highlight = []
        not_found = 0
        for l in self.Lenses:
            if np.abs(event.x - l.x) > 40 and np.abs(event.y - self.w / 2.) > (l.d / 2.):
                pass
            else:
                not_found = 1
                highlight = l
        for o in self.ob:
            if np.abs(event.x - o.x) > 40 and np.abs(event.y - self.w / 2.) > (o.h / 2.):
                pass
            else:
                not_found = 2
                highlight = o
        if not_found == 0:
            if self.selectWindow != 0:
                self.selectWindow[0].destroy()
            return
        elif not_found == 1:
            if self.selectWindow != 0:
                self.selectWindow[0].destroy()
            t = Toplevel()
            t.wm_title("About Me: Lens")

            r1frame = Frame(t)
            er1 = Entry(r1frame)
            er1.insert(0, str(highlight.r1))
            er1.pack(side=RIGHT)
            lr1 = Label(r1frame, text='right radius of curvature: ')
            lr1.pack(side=LEFT)
            r1frame.pack()

            r2frame = Frame(t)
            er2 = Entry(r2frame)
            er2.insert(0, str(highlight.r2))
            er2.pack(side=RIGHT)
            lr2 = Label(r2frame, text='left radius of curvature: ')
            lr2.pack(side=LEFT)
            r2frame.pack()

            fframe = Frame(t)
            ef = Entry(fframe)
            ef.insert(0, str(highlight.f))
            ef.pack(side=RIGHT)
            lf = Label(fframe, text='focal length: ')
            lf.pack(side=LEFT)
            fframe.pack()

            nframe = Frame(t)
            en = Entry(nframe)
            en.insert(0, str(highlight.n))
            en.pack(side=RIGHT)
            ln = Label(nframe, text='index of refraction: ')
            ln.pack(side=LEFT)
            nframe.pack()

            sframe = Frame(t)
            es = Entry(sframe)
            es.insert(0, str(highlight.t))
            es.pack(side=RIGHT)
            ls = Label(sframe, text='thickness: ')
            ls.pack(side=LEFT)
            sframe.pack()

            xframe = Frame(t)
            ex = Entry(xframe)
            ex.insert(0, str(highlight.x))
            ex.pack(side=RIGHT)
            lx = Label(xframe, text='x position: ')
            lx.pack(side=LEFT)
            xframe.pack()

            dframe = Frame(t)
            ed = Entry(dframe)
            ed.insert(0, str(highlight.d))
            ed.pack(side=RIGHT)
            lh = Label(dframe, text='height: ')
            lh.pack(side=LEFT)
            dframe.pack()

            mframe = Frame(t)
            em = Entry(mframe)
            em.insert(0, str(highlight.matrix))
            em.pack(side=RIGHT)
            lm = Label(mframe, text='ray-tracing matrix: ')
            lm.pack(side=LEFT)
            mframe.pack()

            t.geometry('300x200-200+450')
            button = Button(
                t, text="Edit", fg="black",
                command=lambda: self.edit_lens(highlight, ex.get(), ed.get(),en.get(),er1.get(),er2.get(),es.get())
            )
            button.pack(side=TOP)
            self.selectWindow = [t,ex]

        elif not_found == 2:
            if self.selectWindow != 0:
                self.selectWindow[0].destroy()
            t = Toplevel()
            t.wm_title("About Me: Object")

            xframe = Frame(t)
            ex = Entry(xframe)
            ex.insert(0, str(highlight.x))
            ex.pack(side=RIGHT)
            lx = Label(xframe, text='x position: ')
            lx.pack(side=LEFT)
            xframe.pack()

            hframe = Frame(t)
            eh = Entry(hframe)
            eh.insert(0, str(highlight.h))
            eh.pack(side=RIGHT)
            lh = Label(hframe, text='height: ')
            lh.pack(side=LEFT)
            hframe.pack()

            thframe = Frame(t)
            eth = Entry(thframe)
            eth.insert(0,str(0.0))
            eth.pack(side=RIGHT)
            lth = Label(thframe, text='ray angles: ')
            lth.pack(side=LEFT)
            thframe.pack()

            t.geometry('300x200-200+450')
            button = Button(
                t, text="Edit", fg="black",
                command=lambda: self.edit_object(highlight,eh.get(),ex.get(),eth.get())
            )
            button.pack(side=TOP)
            self.selectWindow = [t, ex, eh]

    def edit_object(self, old_ob, hn, xn, thetasn):  # redraws an object if its parameters are modified
        old_ob.h = int(float(hn))
        old_ob.x = int(float(xn))
        if thetasn == '-999':
            old_ob.theta = []
            old_ob.theta.append(0.0)
        else:
            old_ob.theta.append(float(thetasn))
        self.canv.delete(ALL)
        self.initialize(self.canv)
        for l in self.Lenses:
            l.draw(self.canv)
        for o in self.ob:
            o.draw(self.canv)
        self.generate_ray(self.canv)

    def edit_lens(self,old_lens,xn,hn,nn,r1n,r2n,sn):  # redraws a lens if its parameters are modified
        old_lens.d = int(float(hn))
        old_lens.x = int(xn)
        old_lens.n = float(nn)
        old_lens.r1 = int(r1n)
        old_lens.r2 = int(r2n)
        old_lens.t = int(float(sn))
        if int(float(sn)) != 0:
            old_lens.thin_lens = False
        if int(float(sn)) == 0:
            old_lens.thin_lens = True
        if old_lens.thin_lens:
            old_lens.f = old_lens.focalpt(nn, r1n, r2n)
            old_lens.matrix = old_lens.tmthinlens(old_lens.f)
        if not old_lens.thin_lens:
            old_lens.matrix = old_lens.thicklens(1.0, float(nn), int(r1n), int(r2n), int(float(sn)))
            old_lens.f = 10.
        self.canv.delete(ALL)
        self.initialize(self.canv)
        for l in self.Lenses:
            l.draw(self.canv)
        for o in self.ob:
            o.draw(self.canv)
        self.generate_ray(self.canv)

    def left_drag(self, event):  # allows optical elements to be dragged around
        Ltemp = []
        Otemp = []

        Lmodify = lens
        Omodify = obj

        if len(self.Lenses) == 0 and len(self.ob) == 0:
            return
        not_found = 0
        for l in self.Lenses:
            if np.abs(event.x - l.x) > 40 and np.abs(event.y - self.w / 2.) > (l.d / 2.):
                Ltemp.append(l)
            else:
                not_found = 1
                Lmodify = l
        for o in self.ob:
            if np.abs(event.x - o.x) > 40 and np.abs(event.y - self.w / 2.) > (o.h / 2.):
                Otemp.append(o)
            else:
                not_found = 2
                Omodify = o
        if not_found == 0:
            return
        if not_found == 1:
            Lmodify.x = event.x
            self.Lenses = Ltemp
            self.Lenses.append(Lmodify)
            if self.selectWindow != 0:
                self.selectWindow[1].delete(0, END)
                self.selectWindow[1].insert(0, str(event.x))
        if not_found == 2:
            Omodify.x = event.x
            self.ob = Otemp
            self.ob.append(Omodify)
            if self.selectWindow != 0:
                self.selectWindow[1].delete(0, END)
                self.selectWindow[1].insert(0, str(event.x))

        self.canv.delete(ALL)
        self.initialize(self.canv)
        for l in self.Lenses:
            l.draw(self.canv)
        for o in self.ob:
            o.draw(self.canv)
        self.generate_ray(self.canv)

    def right_click(self, event):  # deletes optical element if it is right clicked
        Ltemp = []
        Otemp = []
        for l in self.Lenses:
            if np.abs(event.x - l.x) > 20 and np.abs(event.y - self.w / 2.) > (l.d / 2.):
                Ltemp.append(l)
        for o in self.ob:
            if np.abs(event.x - o.x) > 20 and np.abs(event.y - self.w / 2.) > (o.h / 2.):
                Otemp.append(o)
        self.Lenses = Ltemp
        self.ob = Otemp
        self.canv.delete(ALL)
        self.initialize(self.canv)
        for l in self.Lenses:
            l.draw(self.canv)
        for o in self.ob:
            o.draw(self.canv)

w = Display.w  # these last lines of code set the whole thing into motion and create the instance of display
h = Display.h
root = Tk()
root.title('CAPSTONE PROJECT by Matthew Shinner and Matthew Chow  - 12/9/2016')
root.geometry(str(w)+'x'+str(h+152)+'+0+100')
app = Display(root)

root.mainloop()

