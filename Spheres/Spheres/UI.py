import pygame,sys,os
import GameBoard

class UI:
    def __init__(self, board):
        self.turnImages = {}
        self.specialImages = {}
        self.startingImages = {}
        
        self.screen = None

        self.objectList = []
        self.theBoard = board
        return super().__init__()

    def loadImages(self):
        cwd = os.getcwd()
        for root, dirs, files in os.walk(cwd+"\\Assets\\Cards\\Special",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Cards\\Special\\" + filename
                self.specialImages[name] = pygame.image.load(path)
        
        for root, dirs, files in os.walk(cwd+"\\Assets\\Cards\\StartingLocations",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Cards\\StartingLocations\\" + filename
                self.startingImages[name] = pygame.image.load(path)

        for root, dirs, files in os.walk(cwd+"\\Assets\\Cards\\Turn",topdown=False):
            for filename in files:
                name = filename.split(".")[0]
                path = cwd + "\\Assets\\Cards\\Turn\\" + filename
                self.turnImages[name] = pygame.image.load(path)
        #imagerect = self.specialImages["S_AirSu"].get_rect()
        #while 1:
        #    red = 250,0,0
        #    black = 0,0,0
        #    self.screen.fill(black)
        #    self.screen.blit(self.specialImages["S_AirSu"], imagerect)
        #    pygame.display.flip()
        return 0

    def startUI(self):
        pygame.init()

        size = width, height = 1360, 768
        #speed = [2, 2]
        black = 0, 0, 0

        self.screen = pygame.display.set_mode(size)

        

        #while 1:
        #    for event in pygame.event.get():
        #        if event.type == pygame.QUIT: sys.exit()

        #    ballrect = ballrect.move(speed)
        #    if ballrect.left < 0 or ballrect.right > width:
        #        speed[0] = -speed[0]
        #    if ballrect.top < 0 or ballrect.bottom > height:
        #        speed[1] = -speed[1]

        #    screen.fill(black)
        #    screen.blit(ball, ballrect)
        #    pygame.display.flip()

    def CreatePanels(self):
        theUI = self
        self.objectList.append(UI_SpecialDeck(theUI))

    def update(self):
        for i in self.objectList:
            i.update()

class UI_Panel:
    def __init__(self, UI):
        self.theUI = UI
        self.background = None
        self.height = None
        self.width = None
        self.top = None
        self.left = None

class UI_Map(UI_Panel):
    def __init__(self, UI):
        UI_Panel.__init__(UI)
        return super().__init__(**kwargs)

class UI_SpecialDeck(UI_Panel):
    def __init__(self, UI):
        super().__init__(UI)
        self.background = 220,120,0
        self.top = 540
        self.left = 0
        self.width = 270
        self.height = 230

        self.specialDeck = pygame.transform.scale(self.theUI.specialImages["S_BACK"],(57,79))
        self.specialDeckRect = pygame.Rect(74,50,57,79)
        self.topDiscardDeck = None

    def update(self):
        if len(self.theUI.theBoard.discard_deck) > 0:
            original = self.theUI.theBoard.discard_deck[0]
            #self.topDiscardDeck = pygame.transform.scale()

        self.draw()
        

    def draw(self):
        pygame.draw.rect(self.theUI.screen, self.background, [self.left, self.top, self.width, self.height])
        self.theUI.screen.blit(self.specialDeck, self.specialDeckRect.move(self.left,self.top))
        pygame.display.flip()
        


class UI_Hand(UI_Panel):
    def __init__(self, UI):
        UI_Panel.__init__(UI)
        return super().__init__(**kwargs)

    def update(self):
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

