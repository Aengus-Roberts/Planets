import random
import time
from vpython import *
import sqlite3
import sys


####################
# Defining Classes #
####################

class CelestialObject:
    # Base Class for all objects

    obCount = 0

    def __init__(self, name, mass, x, y, z, xVel, yVel, zVel, radius):
        self.Name = name
        self.immutableMass = mass
        self.Mass = mass
        self.Vector = vector(x, y, z)
        self.Velocity = vector(xVel, yVel, zVel)
        self.X = x
        self.Y = y
        self.Z = z
        self.XV = xVel
        self.YV = yVel
        self.ZV = zVel
        self.Radius = radius
        self.sphere = sphere(pos=vector(x, y, z), radius=radius, make_trail=True)
        CelestialObject.obCount += 1

    def updatePos(self):
        self.sphere.pos += self.Velocity

    def updateVel(self, planetDictionary):
        self.Velocity += TotalSum(planetDictionary, self)

    def getXpos(self):
        return self.X

    def getYpos(self):
        return self.Y

    def getZpos(self):
        return self.Z


class Planet(CelestialObject):
    planetCount = 0

    def __init__(self, name, mass, x, y, z, xVel, yVel, zVel, radius):
        CelestialObject.__init__(self, name, mass, x, y, z, xVel, yVel, zVel, radius)
        Planet.planetCount += 1


class RockyPlanet(Planet):
    rockCount = 0

    def __init__(self, name, mass, x, y, z, xVel, yVel, zVel, radius):
        Planet.__init__(self, name, mass, x, y, z, xVel, yVel, zVel, radius)
        RockyPlanet.rockCount += 1
        if self.Name == "Earth":
            self.sphere.texture = textures.earth
        elif self.Name == "Mars":
            self.sphere.color = color.red
            self.sphere.texture = textures.rough
        elif self.Name == "Venus":
            self.sphere.color = color.orange
            self.sphere.texture = textures.rough
        else:
            self.sphere.texture = textures.rough


class Star(CelestialObject):
    starCount = 0

    def __init__(self, name, mass, x, y, z, xVel, yVel, zVel, radius):
        CelestialObject.__init__(self, name, mass, x, y, z, xVel, yVel, zVel, radius)
        Star.starCount += 1
        self.sphere.color = color.orange


class GasPlanet(Planet):
    gasPlanetCount = 0

    def __init__(self, name, mass, x, y, z, xVel, yVel, zVel, radius):
        Planet.__init__(self, name, mass, x, y, z, xVel, yVel, zVel, radius)
        GasPlanet.gasPlanetCount += 1
        if self.Name == "Jupiter":
            self.sphere.color = color.orange
            self.sphere.texture = textures.wood_old
        elif self.Name == "Saturn":
            self.sphere.color = color.orange
            self.sphere.texture = textures.wood
        elif self.Name == "Uranus":
            self.sphere.color = color.blue
            self.sphere.texture = textures.wood_old
        elif self.Name == "Neptune":
            self.sphere.color = color.blue
            self.sphere.texture = textures.wood
        else:
            self.sphere.texture = textures.metal
            x = random.randint(0, 1)
            if x == 1:
                self.sphere.color = color.blue
            else:
                self.sphere.color = color.orange


##################
# Physics Engine #
##################

def TotalSum(dictionary, object):
    sum = vector(0, 0, 0)
    for i in dictionary:
        if object != dictionary[i]:
            sum += Newton2(
                Force(object.sphere.pos.x, object.sphere.pos.y, object.sphere.pos.z, dictionary[i].sphere.pos.x,
                      dictionary[i].sphere.pos.y,
                      dictionary[i].sphere.pos.z, object.Mass, dictionary[i].Mass),
                object.Mass)
    return sum


def Dist(DeltaX, DeltaY, DeltaZ):  # The distance between 2 Points, 3D Pythagoras
    return ((DeltaX) ** 2 + (DeltaY) ** 2 + (DeltaZ) ** 2) ** 0.5


def RadVector(Ax, Ay, Az, Bx, By, Bz):  # The vector between 2 Points
    return vector(Differance(Bx, Ax), Differance(By, Ay), Differance(Bz, Az))


def Differance(x, y):
    return x - y


def Force(Ax, Ay, Az, Bx, By, Bz, AMass, BMass):  # Returns the Force A and B exert on each other as a vector
    G = 6.67408 * (10 ** -11)
    xDist = Differance(Bx, Ax)
    yDist = Differance(By, Ay)
    zDist = Differance(Bz, Az)
    Distance = Dist(xDist, yDist, zDist)
    TotalForce = (G * AMass * BMass) / (Distance ** 2)
    ForcePerDistance = TotalForce / Distance

    return RadVector(Ax, Ay, Az, Bx, By, Bz) * ForcePerDistance


def Newton2(F, M):
    return F / M


####################
# Creating Planets #
####################

def Load(planetDictionary, file):
    connection = sqlite3.connect(file)

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM 'Planets Table' ")
    print("fetchall:")
    result = cursor.fetchall()
    for r in result:
        print(r[1])
        Name = r[1]
        Mass = r[2]
        x = r[3]
        y = r[4]
        z = r[5]
        Radius = r[6]
        xVel = r[7]
        yVel = r[8]
        zVel = r[9]
        Type = r[10]
        id = r[0]
        if file != "EarthMoon.db":
            if Type == "Star":
                planetDictionary[id] = Star(Name, Mass, x, y, z, xVel, yVel, zVel, Radius * 50)
            if Type == "Gas":
                planetDictionary[id] = GasPlanet(Name, Mass, x, y, z, xVel, yVel, zVel, Radius * 500)
            if Type == "Rock":
                planetDictionary[id] = RockyPlanet(Name, Mass, x, y, z, xVel, yVel, zVel, Radius * 500)
        else:
            if Type == "Star":
                planetDictionary[id] = Star(Name, Mass, x, y, z, xVel, yVel, zVel, Radius)
            if Type == "Gas":
                planetDictionary[id] = GasPlanet(Name, Mass, x, y, z, xVel, yVel, zVel, Radius)
            if Type == "Rock":
                planetDictionary[id] = RockyPlanet(Name, Mass, x, y, z, xVel, yVel, zVel, Radius)

    cursor.close()

    return (planetDictionary)


#############
# Menu Code #
#############

def ChoiceMenu(planetDictionary):
    scene.caption = "\n"
    time.sleep(2)
    menubox = box(color=color.blue)
    if menubox.visible == False:
        menubox.visible = True
    Welcome = wtext(text="\n \n         Welcome to The Solar System Simulator \n")
    Welcome = wtext(text="")
    wtext(
        text="Camera Instruction \n Scroll to zoom the Camera \n Two finger click and drag to rotate the Camera \n Shift-click and drag to pan the Camera \n \n")
    button(bind=lambda self: LoadButton(menubox), text='Load')
    scene.append_to_caption('\n\n')
    button(bind=Quit, text='Quit?')
    scene.append_to_caption('\n\n')


def LoadButton(menubox):
    print("loading...")
    wtext(text="Select a File:\n")
    button(bind=lambda self: LoadFile(menubox, "SS1.db"), text='Solar System')
    button(bind=lambda self: LoadFile(menubox, "ProximaCentauri.db"), text='Binary System')
    button(bind=lambda self: LoadFile(menubox, "EarthMoon.db"), text='Earth and Moon')
    button(bind=lambda self: No(menubox), text="Back")


def Quit():
    print("Are you sure?")
    wtext(text='Are you sure?')
    scene.append_to_caption('\n')
    button(bind=Yes, text='Yes')
    button(bind=No, text="No")


def Yes():
    wtext(text="program ended, please close window")
    time.sleep(2)
    exit()


def No(menubox):
    scene.caption = "\n"
    wtext(
        text="Camera Instruction \n Scroll to zoom the Camera \n Two finger click and drag to rotate the Camera \n Shift-click and drag to pan the Camera \n \n")
    button(bind=lambda self: LoadButton(menubox), text='Load')
    scene.append_to_caption('\n\n')
    button(bind=Quit, text='Quit?')
    scene.append_to_caption('\n\n')


def Back(planetDictionary):
    print("Are you sure?")
    backText = wtext(text='\n\n Are you sure?')
    scene.append_to_caption('\n')
    returnButton = button(bind=lambda self: Return(planetDictionary),
                          text='Yes')
    UndoButton = button(bind=lambda self: BackOne(self, backText, returnButton), text="No")


def BackOne(s, text, otherbutton):
    s.delete()
    text.text = ""
    otherbutton.delete()


def Return(planetDictionary):
    scene.title_anchor = ""
    scene.caption = ""
    global running
    running = False
    for object in planetDictionary:
        planetDictionary[object].sphere.visible = False
        planetDictionary[object].sphere.clear_trail()
    ChoiceMenu(planetDictionary)


def LoadFile(menubox, file):
    planetDictionary = {}
    scene.caption = ''
    menubox.visible = False
    Dictionary = Load(planetDictionary, file)
    Main(Dictionary)


def Run(b, planetDictionary):
    global running
    running = not running
    if running:
        b.text = "Pause"
        print("Playing")
        positionalUpdate(planetDictionary)
    else:
        b.text = "Run"
        print("paused")


def MassEffect(s, planetDictionary, menulist, wt):
    wt.text = 'Mass = {} Times'.format(10 ** s.value)
    if menulist.index > 0:
        planetDictionary[menulist.index].Mass = (planetDictionary[menulist.index].immutableMass * (10 ** (s.value)))
        print(planetDictionary[menulist.index].Mass)


def M(m):
    pass


def positionalUpdate(planetDictionary):
    while running == True:
        for key in planetDictionary:
            planetDictionary[key].updatePos()
            planetDictionary[key].updateVel(planetDictionary)


#################
# Calls Planets #
#################

def Main(planetDictionary):
    print(running)
    scene.append_to_caption('')
    print(planetDictionary)
    pause = button(text="Pause", bind=lambda self: Run(self, planetDictionary))
    scene.append_to_caption('\n\n')
    backButton = button(bind=lambda self: Back(planetDictionary), text="Back")
    scene.append_to_caption('\n\n')
    wt = wtext(text=("Mass = 1 Times"))
    scene.append_to_caption('\n')
    names = ['Choose an object']
    for item in planetDictionary:
        names.append(planetDictionary[item].Name)
    menulist = menu(choices=names, index=0, bind=M)
    scene.append_to_caption('\n')
    massSlider = slider(min=-5, max=5, value=1, length=220, top=10,
                        bind=lambda self: MassEffect(self, planetDictionary, menulist, wt),
                        right=15)

    if running == True:
        positionalUpdate(planetDictionary)


running = False
planetDictionary = {}
scene = canvas()
ChoiceMenu(planetDictionary)
