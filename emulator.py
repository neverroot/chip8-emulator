import pygame
import random

BLACK = [255,255,255]
WHITE = [0,0,0]

# Chip 8 emulator
class Emulator():
    def __init__(self,rom_bytes):
        assert(len(rom_bytes) < 0x4096)
        self.rom = rom_bytes
        self.opcodes = [int.from_bytes(self.rom[i:i+2], 'big') for i in range(0,len(self.rom),2) ]
        self.memory    = [0]*4096
        self.stack     = []
        self.pc        = 0x200
        self.I         = 0x0
        # registers
        self.V = [0 for i in range(16)]

        # Display
        self.grid = [ [ random.randint(0,1) for i in range(64) ] for i in range(32) ]
        self.scale = 10
        self.width = 64
        self.height = 32
        self.clock = pygame.time.Clock()
        self.screen = self.init_display()

    def debug(self):
        print(f"I: {hex(self.I)}")
        for i,reg in enumerate(self.V):
            print(f"V{i}={hex(reg)} ", end='')
        print("")
        print(f"> {hex(self.pc)}        ",end ='')
        print("0x{:04x}".format(self.opcodes[-1]))
        if i==10:
            exit()

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
            self.parse(self.opcodes.pop())
            self.clock.tick(3000)
            self.display()
            self.grid = [ [ random.randint(0,1) for i in range(64) ] for i in range(32) ]  

    def parse(self,opcode):
        self.debug()
        # maybe parse everything I need before if-tree
        # cmd = opcode >> 12 == 0x0:        
        if opcode >> 12 == 0x0:
            if opcode == 0x00e0:
                self.grid = [ [ 0 for i in range(64) ] for i in range(32) ] 
                print("Clear the screen")
            elif opcode == 0x00ee:
                pc = stack.pop()
                print("Return from subroutine")
            else:
                val = opcode & 0x0fff
                pc = val
                print(f"Execute at addr {hex(val)}")
        # if in 0x1NNN bucket
        elif opcode >> 12 == 0x1:
            val = opcode & 0x0fff
            pc = val
            print(f"Jump to address {hex(val)}")
        # if in 0x6NNN bucket
        elif opcode >> 12 == 0x6:
            reg = (opcode & 0x0f00) >> 8
            val = (opcode & 0x00ff)
            self.V[reg] = val
            print(f"Store {hex(val)} in V{reg}")
        # if in 0x7NNN bucket
        elif opcode >> 12 == 0x7:
            reg = (opcode & 0x0f00) >> 8
            val = (opcode & 0x00ff)
            self.V[reg] += val
            print(f"Add {val} to V{reg}")  
        # if in 0xANNN bucket
        elif opcode >> 12 == 0xA:
            val = (opcode & 0x0fff)
            self.I = val
            print(f"Store {hex(val)} in I")
        # if in 0xDNNN bucket
        elif opcode >> 12 == 0xD:
            x = (opcode & 0x0f00)
            y = (opcode & 0x00f0)
            n = (opcode & 0x000f)
            print(f"Draw {n} bytes starting at {x},{y} from address I: {hex(self.I)}")
        self.pc += 0x2
        print("-" * 0x80)
    

