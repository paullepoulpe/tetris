#!/usr/bin/python2.7
import math
import random
import pygame
from pygame.locals import *

# Set up the constants
# Colors
WHITE  = (255, 255, 255)
BLACK  = ( 0 ,   0,   0)
DARK   = (40 ,  40,  40)
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
BLUE   = (  0,   0, 255)
YELLOW = (  0, 255, 255)
ORANGE = (255, 255,   0)

# Geometry
PIECE_SIZE = 35
BORDER_SIZE = 5 
def toPixel(position):
        (x, y) = position
        pixelX = x * PIECE_SIZE + BORDER_SIZE
        pixelY = y * PIECE_SIZE + BORDER_SIZE
        return (pixelX, pixelY)


# Mapping from keys to moves
MOVES = {
    pygame.K_DOWN  : (  0,  1), 
    pygame.K_LEFT  : ( -1,  0),
    pygame.K_RIGHT : (  1,  0),
    }



# Load images
background = pygame.image.load("resources/images/background.png")

class Debris:
    " Debris class for non moving parts "
    
    def __init__(self, position, color):
        self.position = position
        self.color = color

    def draw(self, screen):
        (x, y) = toPixel(self.position)
        screen.fill(self.color, (x, y, PIECE_SIZE, PIECE_SIZE))
        pygame.draw.rect(screen, BLACK, (x, y, PIECE_SIZE, PIECE_SIZE), 2)

    def down(self):
        (x, y) = self.position
        return Debris((x, y + 1), self.color)

    def getHeight(self):
        return self.position[1]

    def containsPosition(self, position):
        return self.position == position

    def overlaps(self, piece):
        return piece.containsPosition(self.position)

class Piece:
    " A common interface for pieces "

    def __init__(self, position):
        self.blocks = []
        self.color = WHITE

    def turn(self, game):
        oldBlocks = self.blocks
        self.blocks = []
        (c1, c2) = oldBlocks[0] # Center of the piece
        for block in oldBlocks:
            (x, y) = block
            newY = x - c1 + c2
            newX = c2 - y + c1
            self.blocks.append((newX, newY))
             
        # If the result is not valid 
        if not self.isValidPiece(game) :
            self.blocks = oldBlocks
            return False
        else:
            return True
    
    def isValidPiece(self, game):
        outOfGame = any( not game.inBounds(block) for block in self.blocks )
        overlap = any( d.overlaps(self) for d in  game.allDebris() ) 
        return not outOfGame and not overlap

    def move(self, game, direction):
        # Save blocks in case move is not allowed
        oldBlocks = self.blocks

        # Map new set of blocks after move
        (dx, dy) = direction
        self.blocks = [ (x + dx, y + dy) for (x, y) in  self.blocks ]          
        
        # If the result is not valid 
        if not self.isValidPiece(game) :
            self.blocks = oldBlocks
            return False
        else:
            return True

    def containsPosition(self, position):
        return any( block == position for block in self.blocks )

    def overlaps(self, other):
        return any( other.containsPosition(block) for block in self.blocks )

    def draw(self, screen):
        for block in self.blocks:
            (x, y) = toPixel(block)
            screen.fill(self.color, (x, y, PIECE_SIZE, PIECE_SIZE))
            pygame.draw.rect(screen, BLACK, (x, y, PIECE_SIZE, PIECE_SIZE), 2)


    def getDebris(self):
        return [ Debris(block, self.color) for block in self.blocks ]


class TPiece(Piece):
    " The T shaped piece "
    ###
     #
    
    def __init__(self, position):
        Piece.__init__(self, position)
        (x, y) = position
        self.blocks.append((x , y))
        self.blocks.append((x - 1, y))
        self.blocks.append((x + 1, y))
        self.blocks.append((x, y + 1))
        self.center = (x, y)
        self.color = BLUE
        

class LPiece(Piece):
    " The L shaped piece "
    ####
    
    def __init__(self, position):
        Piece.__init__(self, position)
        (x, y) = position
        self.blocks.append((x , y))
        self.blocks.append((x - 1, y))
        self.blocks.append((x + 1, y))
        self.blocks.append((x + 2, y))
        self.color = WHITE 
    
class OPiece(Piece):
    " The O shaped piece "
    ##
    ##
    
    def __init__(self, position):
        Piece.__init__(self, position)
        (x, y) = position
        self.blocks.append((x , y))
        self.blocks.append((x + 1, y))
        self.blocks.append((x , y + 1))
        self.blocks.append((x + 1, y + 1))
        self.color = DARK 

class PPiece(Piece):
    " The P shaped piece "
    #
    ###
    
    def __init__(self, position):
        Piece.__init__(self, position)
        (x, y) = position
        self.blocks.append((x , y))
        self.blocks.append((x - 1, y))
        self.blocks.append((x + 1, y))
        self.blocks.append((x - 1, y + 1))
        self.color = GREEN

class QPiece(Piece):
    " The Q shaped piece "
      #
    ###
    
    def __init__(self, position):
        Piece.__init__(self, position)
        (x, y) = position
        self.blocks.append((x , y))
        self.blocks.append((x - 1, y))
        self.blocks.append((x + 1, y))
        self.blocks.append((x + 1, y + 1))
        self.color = RED 

        
class SPiece(Piece):
    " The S shaped piece "
     ##
    ##
    
    def __init__(self, position):
        Piece.__init__(self, position)
        (x, y) = position
        self.blocks.append((x , y))
        self.blocks.append((x - 1, y))
        self.blocks.append((x , y + 1))
        self.blocks.append((x + 1, y + 1))
        self.color = YELLOW

class ZPiece(Piece):
    " The Z shaped piece "
    ##
     ##
    
    def __init__(self, position):
        Piece.__init__(self, position)
        (x, y) = position
        self.blocks.append((x , y))
        self.blocks.append((x , y -1))
        self.blocks.append((x + 1, y))
        self.blocks.append((x + 1, y + 1))
        self.color = ORANGE 


# All possible pieces in the game
PIECES = [ TPiece, OPiece, PPiece, QPiece, LPiece, SPiece, ZPiece ]
class Game:
    " Class representing the current game "

    def __init__(self, bounds):
        (width, height) = bounds
        self.width = width
        self.height = height
        self.pixelWidth = width * PIECE_SIZE + 2 * BORDER_SIZE
        self.pixelHeight = height * PIECE_SIZE + 2 * BORDER_SIZE
        self.screen = pygame.display.set_mode((self.pixelWidth, self.pixelHeight))
        self.debris = []
        self.currentPiece = self.randomPiece()
        self.losing = False

    def allDebris(self):
        return self.debris

    def hasDebrisAt(self, position):
        return any(x.containsPosition(position) for x in self.debris)

    def checkLines(self):
        for line in range(self.height):
            if all(self.hasDebrisAt((x, line)) for x in range(self.width)):
                self.removeLine(line)

    def removeLine(self, lineNo):
        under = [ d for d  in self.debris if d.getHeight() > lineNo ]
        over = [ d.down() for d in self.debris if d.getHeight() < lineNo ]
        self.debris = under + over

    def redraw(self):
        self.screen.fill(0)
        self.screen.blit(background, (0,0))
        
        firstX = BORDER_SIZE
        firstY = BORDER_SIZE
        lastX = self.pixelWidth - BORDER_SIZE
        lastY = self.pixelHeight - BORDER_SIZE
        for x in range(firstX, lastX + 1, PIECE_SIZE):
            pygame.draw.line(self.screen, BLACK, (x, firstY), (x, lastY), 4)

        for y in range(firstY, lastY + 1, PIECE_SIZE):
            pygame.draw.line(self.screen, BLACK, (firstX, y), (lastX, y), 4)
        
        for debris in self.debris:
            debris.draw(self.screen)
        
        self.currentPiece.draw(self.screen)
        pygame.display.flip()

    def move(self, direction):
        valid = self.currentPiece.move(self, direction)
        self.losing = self.losing and not valid
        return valid

    def inBounds(self, position):
        (x, y) = position
        return (x in range(self.width)  and y in range(self.height))

    def randomPiece(self):
        index = random.randint(0, len(PIECES) - 1)
        return PIECES[index]((self.width/2, 1))

    def newPiece(self):
        for debris in self.currentPiece.getDebris():
            self.debris.append(debris)
        self.currentPiece = self.randomPiece() 
        if not self.currentPiece.isValidPiece(game) :
            if self.losing:
                # Lost the game
                return False
            else:    
                # Overlap might be overcome by a move
                # This is simpler than complicated logic that checks
                # is there are any valid moves
                self.losing = True
        return True

    def turnPiece(self):
        self.currentPiece.turn(self)
    

# Initialize the game
pygame.init()
game = Game((8, 15))

# Load music
pygame.mixer.music.load('resources/audio/tetris.wav')
pygame.mixer.music.play(-1, 0.0)

## Check if the player has closed the game
def check_quit(event):
    if event.type == pygame.QUIT:
        pygame.quit() 
        exit(0)

# Main game loop
timer = 200
while 1:
    timer -= 1
    game.redraw()
    
    
    # Loop through the events
    for event in pygame.event.get():
        
        # Check if the event is the X button 
        check_quit(event)

        # Check if the event is a move
        if event.type == pygame.KEYUP: 
            if event.key in MOVES:
                game.move(MOVES[event.key])
            elif event.key == pygame.K_UP:
                game.turnPiece()
            elif event.key == pygame.K_SPACE:
                while game.move(MOVES[pygame.K_DOWN]):
                    pass
                timer = 0
    
    if timer == 0:
        timer = 200
        if not game.move(MOVES[pygame.K_DOWN]):
            if not game.newPiece():
                # Game over, start new game 
                game = Game((8, 15))
            game.checkLines()
