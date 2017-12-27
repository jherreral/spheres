import pygame,sys,os
import GameBoard
from Selection import Selection
import threading
import queue


class UI:
    def __init__(self, receiveQueue, sendQueue):
        self.imageBank = {}
        self.turnImages = {}
        self.specialImages = {}
        self.startingImages = {}
        self.diceImages = {}
        self.theBoard = None
        self.receiveQueue = receiveQueue
        self.sendQueue = sendQueue
        self.targetFramerate = 60

        self.screen = None

        self.objectList = []

    def loadImages(self):
        cwd = os.getcwd()
        self.imageBank["S"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\Cards\\Special",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Cards\\Special\\" + filename
                self.specialImages[name] = pygame.image.load(path)
                self.imageBank["S"][name] = pygame.image.load(path)
        
        self.imageBank["SL"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\Cards\\StartingLocations",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Cards\\StartingLocations\\" + filename
                self.startingImages[name] = pygame.image.load(path)
                self.imageBank["SL"][name] = pygame.image.load(path)

        self.imageBank["T"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\Cards\\Turn",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Cards\\Turn\\" + filename
                self.turnImages[name] = pygame.image.load(path)
                self.imageBank["T"][name] = pygame.image.load(path)

        self.imageBank["UI"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\UI",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\UI\\" + filename
                self.turnImages[name] = pygame.image.load(path)
                self.imageBank["UI"][name] = pygame.image.load(path)

        self.imageBank["MP"]={}
        for root, dirs, files in os.walk(cwd+"\\Assets\\Map",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Map\\" + filename
                self.turnImages[name] = pygame.image.load(path)
                self.imageBank["MP"][name] = pygame.image.load(path)
        #imagerect = self.specialImages["S_AirSu"].get_rect()
        #while 1:
        #    red = 250,0,0
        #    black = 0,0,0
        #    self.screen.fill(black)
        #    self.screen.blit(self.specialImages["S_AirSu"], imagerect)
        #    pygame.display.flip()
        return 0

    def FindImage(self,name):
        if "S_"+name in self.imageBank["S"]:
            return "S_"+name
        #self.imageBank["S"]["S_"+name]
        if "SL_"+name in self.imageBank["SL"]:
            return "SL_"+name
        #self.imageBank["SL"]["SL_"+name]
        if "T_"+name in self.imageBank["T"]:
            return "T_"+name
        #self.imageBank["T"]["T_"+name]
        if "UI_"+name in self.imageBank["UI"]:
            return "UI_"+name
        if "MP_"+name in self.imageBank["MP"]:
            return "MP_"+name

    def startUI(self):
        boardReady = False
        while not boardReady:
            if not self.receiveQueue.empty():
                self.theBoard = self.receiveQueue.get()
                self.receiveQueue.task_done()
                boardReady = True

        pygame.init()
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        size = width, height = 1360, 768
        #speed = [2, 2]
        black = 0, 0, 0

        self.screen = pygame.display.set_mode(size)

    def CreatePanels(self):
        theUI = self
        self.objectList.append(UI_SpecialDeck(theUI,0,540,270,230,(220,120,0)))
        self.objectList.append(UI_Map(theUI,260,0,827,568,(0,0,150)))

    def pollQueue(self):
        while not self.receiveQueue.empty():
            somethingFromGB = self.receiveQueue.get()
            typeOfObject = type(somethingFromGB)
            if typeOfObject is Selection:
                typeOfSelection = somethingFromGB.type
                if typeOfSelection == "Card":
                    self.objectList.append(SelectionPanel(somethingFromGB.options,typeOfSelection,self,50,50,640,480,(100,100,0)))
                    self.receiveQueue.task_done()
                if typeOfSelection == "Pause":
                    self.objectList.append(SelectionPanel(somethingFromGB.options,typeOfSelection,self,450,450,200,200,(0,0,100)))
                    self.receiveQueue.task_done()
            if typeOfObject is GameBoard.GameBoard:
                self.theBoard = somethingFromGB
                self.receiveQueue.task_done()

    def update(self):
        self.pollQueue()
        if pygame.event.peek(pygame.QUIT):
            return False
        mouseButtonEvents = pygame.event.get(pygame.MOUSEBUTTONDOWN)
        if mouseButtonEvents:
            lastMouseButtonEvent = mouseButtonEvents[len(mouseButtonEvents)-1]
            for panel in self.objectList:
                if panel.myRect.collidepoint(lastMouseButtonEvent.pos[0],lastMouseButtonEvent.pos[1]):
                    panel.pressed(lastMouseButtonEvent)

        #Start drawing
        self.screen.fill((0,0,0))
        for i in self.objectList:
            if i.jobDone:
                self.objectList.remove(i)
                continue
            i.update()
        pygame.display.flip()

class UI_Panel:
    def __init__(self, UI, left, top, width, height, background):
        self.theUI = UI
        self.background = background
        self.height = height
        self.width = width
        self.top = top
        self.left = left
        self.jobDone = False
        self.objectList = []
        self.myRect = pygame.Rect(self.left,self.top,self.width,self.height)

    def pressed(self,event):
        for object in self.objectList:
            if object.myRect.collidepoint(event.pos[0],event.pos[1]):
                object.pressed()
 
class MP_Zone():
    def __init__(self, name, surf, rect, position, mask):
        self.name = name
        self.surf = surf
        self.rect = rect
        self.position = position
        self.mask = mask


class UI_Map(UI_Panel):
    def __init__(self, UI, left, top, width, height, background):
        super().__init__(UI, left, top, width, height, background)
        self.map = self.theUI.imageBank["MP"]["MP_Board"]
        self.map = pygame.transform.scale(self.map,(self.width,self.height))
        self.zoneList = []
        self.ParseZones()

    def ParseZones(self):
        f = open("MapCoords.csv","r")
        for line in f:
            (name,x,y) = line.split(";")
            x = int(x)
            y = int(y.rstrip())
            surf = self.theUI.imageBank["MP"]["MP_"+name]
            rect = surf.get_rect()
            rect.move_ip(x,y)
            self.zoneList.append(MP_Zone(name,surf,rect,(x,y),pygame.mask.from_surface(surf)))
        f.close()

    def update(self):
        self.theUI.screen.blit(self.map,self.myRect)
        mPos = pygame.mouse.get_pos()
        for zone in self.zoneList:
            maskSize = zone.mask.get_size()
            maskX = mPos[0]-zone.position[0]-self.left
            maskY = mPos[1]-zone.position[1]-self.top
            if maskX in range(0,maskSize[0]) and maskY in range(0,maskSize[1]):
                if zone.mask.get_at((maskX,maskY)):
                    self.theUI.screen.blit(zone.surf, zone.rect.move(self.left,self.top))



class UI_SpecialDeck(UI_Panel):

    def __init__(self, UI, left, top, width, height, background):
        super().__init__(UI, left, top, width, height, background)
        self.objectList.append(UI_Button("specialDeckBtn",self.theUI,74,50,57,79,(self.left,self.top),"S_BACK"))

    def update(self):
        ### Actualiza y dibuja el panel y sus elementos. Cada elemento llama a su propio update y draw.
        if len(self.theUI.theBoard.discard_deck) > 0:
            buttonImage = self.theUI.theBoard.discard_deck[0]
            #self.topDiscardDeck = pygame.transform.scale()

        pygame.draw.rect(self.theUI.screen, self.background, self.myRect)
        for object in self.objectList:
            object.update()

        
class UI_Button:
    def __init__(self,buttonName,UI,left,top,width,height,ref,imageName):
        self.buttonName = buttonName
        self.theUI = UI
        self.height = height
        self.width = width
        self.top = top
        self.left = left
        self.state = 0

        (type,image) = imageName.split("_")
        self.screenLeft = self.left + ref[0]
        self.screenTop = self.top + ref[1]

        self.myRect = pygame.Rect(self.screenLeft,self.screenTop,self.width,self.height)
        self.buttonOff = pygame.transform.scale(self.theUI.imageBank[type][type+"_"+image+"Off"],(self.width,self.height))
        self.buttonHighlight = pygame.transform.scale(self.theUI.imageBank[type][type+"_"+image+"Highlight"],(self.width,self.height))
        self.buttonOn = pygame.transform.scale(self.theUI.imageBank[type][type+"_"+image],(self.width,self.height))
        
    def drawOff(self):
        self.theUI.screen.blit(self.buttonOff, self.myRect)

    def drawHighlight(self):
        self.theUI.screen.blit(self.buttonHighlight, self.myRect)

    def drawOn(self):
        self.theUI.screen.blit(self.buttonOn, self.myRect)

    def pressed(self):
        self.state = 1
        #Some function here

    def update(self):
        if self.state == 1:
            if pygame.event.get(pygame.MOUSEBUTTONUP):
                self.state = 0
                if self.myRect.collidepoint(pygame.mouse.get_pos()):
                    self.drawHighlight()
                else:
                    self.drawOff()
            else:
                self.drawOn()
        else:
            if self.myRect.collidepoint(pygame.mouse.get_pos()):
                self.drawHighlight()
            else:
                self.drawOff()
            
        
        #switcher = {
        #    0: "drawOff",
        #    1: "drawHighlight",
        #    2: "drawOn",
        #}
        #method = getattr(self, switcher[self.state],lambda:"Error")
        ##func = switcher.get(self.state, lambda: "Error")
        #method()

class SelectionPanel(Selection,UI_Panel):
    def __init__(self, options, type, UI, left, top, width, height, background):
        Selection.__init__(self,options,type)
        UI_Panel.__init__(self,UI, left, top, width, height, background)
        
        nOpts = len(self.options)
        if type == "Card":
            self.width = 200+nOpts*378
            self.height = 50+nOpts*526
            for i,objectName in enumerate(self.options):
                self.objectList.append(UI_Button(objectName,self.theUI,100+i*378,50,378,526,(self.left,self.top),self.theUI.FindImage(objectName)))

        if type == "Pause":
            self.width = 200
            self.height = 200
            self.objectList.append(UI_Button(self.options[0],self.theUI,10,10,180,180,(self.left,self.top),self.theUI.FindImage(self.options[0])))
        else:
            self.width = 300
            self.height = 300
    
    def sendSelection(self):
        response = Selection(self.options,self.type)
        response.setSelection(self.selection)
        self.theUI.sendQueue.put(response)

    def update(self):
        ### Actualiza y dibuja el panel de seleccion y sus elementos. Cada elemento llama a su propio update y draw.
        pygame.draw.rect(self.theUI.screen, self.background, self.myRect)
        for button in self.objectList:
            if button.state == 1:
                self.selection = button.buttonName
                self.sendSelection()
                self.jobDone = True
                break
            button.update()


class UI_Hand(UI_Panel):
    
    def __init__(self, UI, left, top, width, height, background):
        super().__init__(UI, left, top, width, height, background)

    def update(self):
        pygame.draw.rect(self.theUI.screen, self.background, [self.left, self.top, self.width, self.height])
        self.getCards()
        self.drawCards()

    def getCards(self):
        pass

    def drawCards(self):
        pass

class UI_Track(UI_Panel):
    def __init__(self, UI):
        UI_Panel.__init__(UI)
        return super().__init__(**kwargs)

    def update(self):
        pass

class UI_PlayerCards(UI_Panel):
    def __init__(self, UI):
        UI_Panel.__init__(UI)
        return super().__init__(**kwargs)

