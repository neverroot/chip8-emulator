import pygame
import random

BLACK = [255,255,255]
WHITE = [0,0,0]

# Chip 8 emulator
class Emulator():
    def __init__(self):
        self.memory    = [0]*4096
        self.pc        = 0x0
        self.I         = 0x0
        self.V = [0 for i in range(16)] #registers
        self.grid = [ [ random.randint(0,1) for i in range(64) ] for i in range(32) ]
        # Display
        self.scale = 10
        self.width = 64
        self.height = 32
        self.clock = pygame.time.Clock()
        self.screen = self.init_display()

    def init_display(self):
        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT+1, int(1000 / 60))
        screen = pygame.display.set_mode([self.width * self.scale, self.height * self.scale])
        screen.fill(BLACK)
        pygame.display.flip()
        return screen
    
    def display(self):
        for i in range(0,len(self.grid)):
            for j in range(0,len(self.grid[0])):
                cellColor = BLACK
                if self.grid[i][j] == 1:
                    cellColor = WHITE
                pygame.draw.rect(self.screen, cellColor, [j * self.scale, i * self.scale, self.scale, self.scale], 0)
        pygame.display.flip()
    
    def loop(self):
        while True:
            self.clock.tick(300)
            self.display()
            self.grid = [ [ random.randint(0,1) for i in range(64) ] for i in range(32) ]    
    def parse(self,opcode):
        print(hex(opcode).ljust(6,"0"),end=' ')
        if opcode >> 12 == 0x0:
            if opcode == 0x00e0:
                print("Clear the screen")
            if opcode == 0x00ee:
                print("Return from subroutine")
            else:
                print(f"Execute at addr {hex(opcode & 0x0fff)}")
        # if in 0x1NNN bucket
        elif opcode >> 12 == 0x1:
            print(f"Jump to address {hex(opcode & 0x0fff)}")
        # if in 0x6NNN bucket
        elif opcode >> 12 == 0x6:
            val = (opcode & 0x00ff)
            reg = (opcode & 0x0f00) >> 8
            print(f"Store {val} in V{reg}")
        # if in 0x7NNN bucket
        elif opcode >> 12 == 0x7:
            val = (opcode & 0x00ff)
            reg = (opcode & 0x0f00) >> 8
            print(f"Add {val} to V{reg}")  
        # if in 0xANNN bucket
        elif opcode >> 12 == 0xA:
            print("")
        # if in 0xDNNN bucket
        elif opcode >> 12 == 0xD:
            print("") 
