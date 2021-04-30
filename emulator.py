import pygame
import random
import time

BLACK = [255,255,255]
WHITE = [0,0,0]

# Chip 8 emulator
class Emulator():
    def __init__(self,rom_bytes):
        assert(len(rom_bytes) < 0x4096)
        self.rom     = rom_bytes
        self.opcodes = [int.from_bytes(self.rom[i:i+2], 'big') for i in range(0,len(self.rom),2) ]
        self.memory  = [0]*4096
        self.stack   = []
        self.pc      = 0x200
        self.I       = 0x0
        self.loaded  = False
        # 16 registers
        self.V = [0 for i in range(16)]

        # Display
        self.grid = [ [ random.randint(0,1) for i in range(64) ] for i in range(32) ]
        self.scale = 10
        self.width = 64
        self.height = 32
        self.clock = pygame.time.Clock()
        self.screen = self.init_display()

        # Keyboard
        self.init_keyboard()

        # Timers
        self.display_timer = 0
        self.sound_timer   = 0

        # Fonts
        self.fonts = [ 
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]


    def load(self,base=0x200, font=0x50):
        assert(base >= 0x200 and base <= len(self.memory) - len(self.rom))
        assert(font >= 0x0 and font <= (0x200 - len(self.fonts)) )

        # load fonts
        for n in range(len(self.fonts)):
            self.memory[n+font] = self.fonts[n]
        
        # load rom
        for i in range(len(self.rom)):
            self.memory[i+base] = self.rom[i]

        self.pc = base
        self.loaded = True

    def debug(self):
        print(f"I: {hex(self.I)}")
        for i,reg in enumerate(self.V):
            print(f"V{i}={hex(reg)} ", end='')
        print("")
        print(f"> {hex(self.pc)}        ",end ='')
        print("0x{:04x}".format(self.opcodes[0]))

    def init_display(self):
        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT+1, int(1000 / 60))
        screen = pygame.display.set_mode([self.width * self.scale, self.height * self.scale])
        screen.fill(BLACK)
        pygame.display.flip()
        return screen
    
    def init_keyboard(self):
        self.keyDict = {
            49 : 1,    50 : 2,  51 : 3,   52 : 0xc,
            113 : 4,   119 : 5, 101 : 6,  114 : 0xd,
            97 : 7,    115 : 8, 100 : 9,  102 : 0xe,
            122 : 0xa, 120 : 0, 99 : 0xb, 118 : 0xf
        }

    def keyboard_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.USEREVENT + 1:
                self.delay_timer -= 1
            elif event.type == pygame.KEYDOWN:
                try:
                    target = self.keyDict[event.key]
                    print(event.key,target)
                except:
                    pass
            elif event.type == pygame.KEYUP:
                try:
                    target = self.keyDict[event.key]
                    print(event.key,target)
                except:
                    pass
        
    
    def display(self):
        for i in range(0,len(self.grid)):
            for j in range(0,len(self.grid[0])):
                cellColor = BLACK
                if self.grid[i][j] == 1:
                    cellColor = WHITE
                pygame.draw.rect(self.screen, cellColor, [j * self.scale, i * self.scale, self.scale, self.scale], 0)
        pygame.display.flip()
    
    def loop(self):
        assert( self.loaded == True )
        while True:
            #self.debug()
            self.parse(self.memory[self.pc:self.pc+2])
            self.clock.tick(3000)
            self.display()
            time.sleep(.5)

    def parse(self,codes):
        # maybe parse everything I need before if-tree
        opcode = (codes[0] << 8) | codes[1]
        print("[{}]      0x{:04x}".format(hex(self.pc),opcode))
        # cmd = opcode >> 12 == 0x0:        
        if opcode >> 12 == 0x0:
            if opcode == 0x00e0:
                self.grid = [ [ 0 for i in range(64) ] for i in range(32) ] 
                print("Clear the screen")
            elif opcode == 0x00ee:
                self.pc = self.stack.pop()
                print("Return from subroutine")
            else:
                val = opcode & 0x0fff
                self.pc  = val
                print(f"Execute at addr {hex(val)}")
        # if in 0x1NNN bucket
        elif opcode >> 12 == 0x1:
            val = opcode & 0x0fff
            self.pc = val - 2
            print(f"Jump to address {hex(val)}")
        # if in 0x2NNN bucket
        elif opcode >> 12 == 0x2:
            val = opcode & 0x0fff
            self.stack.append(val)
            print(f"Execute subroutine at address {hex(val)}")
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
            print(f"Add {hex(val)} to V{reg}")  
        # if in 0xANNN bucket
        elif opcode >> 12 == 0xA:
            val = (opcode & 0x0fff)
            self.I = val
            print(f"Store {hex(val)} in I")
        # if in 0xDNNN bucket
        elif opcode >> 12 == 0xD:
            x = (opcode & 0x0f00) >> 8
            y = (opcode & 0x00f0) >> 4
            n = (opcode & 0x000f)
            sprite = self.memory[self.I:self.I+n]
            #print(f"Draw {n} bytes starting at ({self.V[x]},{self.V[y]}) reading from address I: {hex(self.I)}")
            print(sprite)
            bns = []
            for val in sprite:
                b = bin(val)[2:].zfill(8)
                bns.append( [ int(b[i],2) for i in range(len(b)) ] )

            regx = self.V[x]
            regy = self.V[y]

            for i in range(len(bns)):
                for j in range(len(bns[0])):
                    self.grid[regy+i][regx+j] ^= bns[i][j]
            

        self.pc += 2
        print("-" * 0x80)
    

