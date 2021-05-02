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
        self.grid = [ [ 0 for i in range(64) ] for i in range(32) ]
        self.scale = 10
        self.width = 64
        self.height = 32
        self.clock = pygame.time.Clock()
        self.screen = self.init_display()

        # Keyboard
        self.init_keyboard()

        # Timers
        self.delay_timer = 0
        self.sound_timer = 0

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
            time.sleep(.1)

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
        # if in 0x3NNN bucket
        elif opcode >> 12 == 0x3:
            regx = (opcode & 0x0f00) >> 8
            nn = opcode & 0x00ff
            if self.V[regx] == nn:
                self.pc += 2
            print(f"Skip following instruction if V{regx} == {hex(opcode & 0x00ff)}")
        # if in 0x4NNN bucket
        elif opcode >> 12 == 0x4:
            regx = (opcode & 0x0f00) >> 8
            nn = opcode & 0x00ff
            if self.V[regx] != nn:
                self.pc += 2
            print(f"Skip following instruction if V{regx} != {hex(opcode & 0x00ff)}")
        # if in 0x5NNN bucket
        elif opcode >> 12 == 0x5:
            assert( (opcode & 0x000f) == 0)
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            if self.V[regx] == self.V[regy]:
                self.pc += 2
            print(f"Skip following instruction if V{regx} == V{regy}")
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
        # if in 0x8NNN bucket
        elif opcode >> 12 == 0x8:
            index = opcode & 0xf
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            # Store
            if index == 0x0:
                self.V[regx] = self.V[regy]
                print(f"Store V{regy} in V{regx}")
            # OR
            if index == 0x1:
                self.V[regx] |= self.V[regy]
                print(f"Store V{regx} | V{regy} in V{regx}")
            # AND 
            if index == 0x2:
                self.V[regx] &= self.V[regy]
                print(f"Store V{regx} & V{regy} in V{regx}")
            # XOR
            if index == 0x3:
                self.V[regx] ^= self.V[regy]
                print(f"Store V{regx} ^ V{regy} in V{regx}")
            # ADD with carry
            if index == 0x4:
                self.V[regx] += self.V[regy]
                self.V[0xf] = 0
                if self.V[regx] > 0xff:
                    self.V[0xf] = 1
                    self.V[regx] = self.V[regx] & 0xff
                print(f"Store V{regx} + V{regy} in V{regx} and set carry flag")
            # Check for borrow
            if index == 0x5:
                tmp = self.V[regx] - self.V[regy]
                self.V[0xf] = 1
                if tmp < 0:
                    self.V[0xf] = 0
                    self.V[regx] = abs(self.V[regx])
                print(f"Check if borrow occurs in V{regx}-V{regy} and set carry flag in Vf")
            # Shift right 1 bit
            if index == 0x6:
                self.V[0xf]  = self.V[regy] & 0xf
                self.V[regx] = self.V[regy] >> 1
                print(f"V{regx} = V{regy} >> 1 with least significant bit saved in Vf")
            # SUB with borrow
            if index == 0x7:
                self.V[regx] -= self.V[regy]
                self.V[0xf]   = 1
                if self.V[regx] < 0:
                    self.V[0xf]  = 0
                    self.V[regx] = abs(self.V[regx])
                print(f"V{regx} -= V{regy} and check set carry flag in Vf")
            # Shift left 1 bit
            if index == 0xe:
                self.V[0xf]  = self.V[regy] >> 12
                self.V[regx] = self.V[regy] << 1
                print(f"V{regx} = V{regy} << 1 with most significant bit saved in Vf")
        # if in 0x9NNN bucket
        elif opcode >> 12 == 0x9:
            if self.V[regx] != self.V[regy]:
                self.pc += 2
            print(f"Skip following instruction if V{regx} != V{regy}")
        # if in 0xANNN bucket
        elif opcode >> 12 == 0xA:
            val = (opcode & 0x0fff)
            self.I = val
            print(f"Store {hex(val)} in I")
        # if in 0xBNNN bucket
        elif opcode >> 12 == 0xb:
            val = opcode & 0x0fff
            self.pc = val + self.V[0]
            self.pc -= 2
            print(f"Jump to address {hex(val)} + V0")
        # if in 0xCNNN bucket
        elif opcode >> 12 == 0xc:
            val = opcode & 0x00ff
            r = random.randint(0,255)
            self.V[regx] = r & val
            print(f"Set V{regx} to random number: {hex(r)} & {hex(val)}")
        # if in 0xDNNN bucket
        elif opcode >> 12 == 0xd:
            x = (opcode & 0x0f00) >> 8
            y = (opcode & 0x00f0) >> 4
            n = (opcode & 0x000f)
            sprite = self.memory[self.I:self.I+n]
            print(f"Draw {n} bytes starting at ({self.V[x]},{self.V[y]}) reading from address I: {hex(self.I)}")
            bns = []
            for val in sprite:
                b = bin(val)[2:].zfill(8)
                bns.append( [ int(b[i],2) for i in range(len(b)) ] )

            regx = self.V[x]
            regy = self.V[y]
            print(bns)
            for i in range(len(bns)):
                for j in range(len(bns[0])):
                    self.grid[(regy+i)][(regx+j)] ^= bns[i][j]
        # if in 0xENNN bucket
        elif opcode >> 12 == 0xe:
            index = opcode & 0x00ff
            if index == 0x9e:
                if V[regx] == 0x1337:
                    self.pc += 2
            if index == 0xa1:
                if V[regx] != 0x1337:
                    self.pc += 2
        # if in 0xFNNN bucket
        elif opcode >> 12 == 0xf:
            index = opcode & 0x00ff
            regx  = (opcode & 0x0f00) >> 8
            if index == 0x07:
                self.V[regx] = self.delay_timer
            if index == 0x0a:
                self.keyboard_handler()
            if index == 0x15:
                self.delay_timer = self.V[regx]
            if index == 0x18:
                self.sound_timer = self.V[regx]
            if index == 0x1e:
                self.I += self.V[regx]
            if index == 0x29:
                self.I = self.V[regx] * 5
            if index == 0x33:
                self.I = 0x1337
            if index == 0x55:
                for i in range(regx+1):
                   self.memory[self.I + i] = self.V[i] 
            if index == 0x65:
                for i in range(regx+1):
                    self.V[i] = self.memory[self.I + i]
        self.pc += 2
        print("-" * 0x80)
    

