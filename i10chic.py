# matrices.py
# Animated simulation of chicane magnets

# Import libraries

import dls_packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# Define matrices to modify the electron beam vector:
# drift and kicker magnets.


class Drifting:


    def __init__(self, STEP):
        self.STEP = STEP

    def increment(self, e):
        drift = np.array([[1,self.STEP],
                          [0,1]])
        return np.dot(drift,e)

    def locate(self,where):
        return where + self.STEP

    def type(self):
        return 'drift'

class Kicker:


    def __init__(self, k, STEP):
        self.k = k
        self.STEP = STEP

    def increment(self, e):
        kick = np.array([0, self.k])
        drift = np.array([[1,self.STEP],
                          [0,1]])
        return np.dot(drift,e) + kick

    def locate(self,where):
        return where + self.STEP

    def type(self):
        return 'kicker'


# Define the insertion device - needs to be added.

class InsertionDevice:


    def __init__(self, STEP):
        self.STEP = STEP

    def increment(self, e):
        drift = np.array([[1,self.STEP],
                          [0,1]])
        return np.dot(drift,e)

    def locate(self,where):
        return where + self.STEP

    def type(self):
        return 'id'

# Send electron vector through chicane magnets at time t.

def timestep(t):

    # Initialise electron beam and position within system
    e_beam = np.array([0,0])
    e_pos = [e_beam[0]]
    where = 0
    s = [where]
    idloc = []
    kickerloc = []

    # Set size of step through chicane
    STEP = 1

    # Strengths of magnets vary by sin function
    strength = [
        np.sin(t*np.pi/100) + 1, -(1.5)*(np.sin(t*np.pi/100) + 1), 
        1, -(1.5)*(np.sin(t*np.pi/100 + np.pi) + 1), 
        np.sin(t*np.pi/100 + np.pi) + 1
        ]

    path = [
        Drifting(STEP),Kicker(strength[0],STEP),
        Drifting(STEP),Kicker(strength[1],STEP),
        Drifting(STEP),InsertionDevice(STEP),
        Drifting(STEP),Kicker(strength[2],STEP),
        Drifting(STEP),InsertionDevice(STEP),
        Drifting(STEP),Kicker(strength[3],STEP),
        Drifting(STEP),Kicker(strength[4],STEP),
        Drifting(STEP),Drifting(STEP)
        ]

    for p in path:
        obj = p.type()
        if obj == 'id':
            idloc.append(p.locate(where))
        if obj == 'kicker':
            kickerloc.append(p.locate(where))
        e_beam = p.increment(e_beam)
        e_pos.append(e_beam[0])
        where = p.locate(where)
        s.append(where)


    return s, e_pos, idloc, kickerloc #also want to return specifically the locations of the magnets and IDs to be plotted :)


# Set up figure, axis and plot element to be animated.
fig = plt.figure()
ax = plt.axes(xlim=(0, 16), ylim=(-2, 5))
line, = ax.plot([], [], lw=1)
idwhere, = ax.plot([], [], 'r.')

# Initialisation function: plot the background of each frame.
def init():
    line.set_data([], [])
    idwhere.set_data([], [])
    return line, idwhere,

# Animation function
def animate(t):
    x = timestep(t)[0]
    y = timestep(t)[1]
    id = timestep(t)[2]
    line.set_data(x, y)
    idwhere.set_data(id, [0,0])
    k1 = plt.axvline(x=timestep(t)[3][0], color='k', linestyle='dashed')
    k2 = plt.axvline(x=timestep(t)[3][1], color='k', linestyle='dashed')
    k3 = plt.axvline(x=timestep(t)[3][2], color='k', linestyle='dashed')
    k4 = plt.axvline(x=timestep(t)[3][3], color='k', linestyle='dashed')
    k5 = plt.axvline(x=timestep(t)[3][4], color='k', linestyle='dashed') # Must be a nicer way...
    return line, idwhere, k1, k2, k3, k4, k5

# Call the animator
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=200, interval=10, blit=True)

plt.show()





