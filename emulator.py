import pygame
from pygame.locals import *
import random
import time
import sys

# RGB color constants
BLACK = [255,255,255]
WHITE = [0,0,0]

# Chip 8 emulator
class Emulator():
    def __init__(self,rom_bytes,debug = False):

        assert(len(rom_bytes) < 0x4096)
        self.debug   = debug
        self.rom     = rom_bytes
        self.memory  = [0]*4096
        self.stack   = []
        self.pc      = 0x200
        self.I       = 0x0
        self.loaded  = False
        # 16 registers
        self.V = [0 for i in range(16)]

        # Display
        self.grid = [ [ 1 for i in range(64) ] for i in range(32) ]
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

    # load fonts and rom into memory
    def load(self,base=0x200, font=0x50):
        assert(base >= 0x200 and base <= len(self.memory) - len(self.rom))
        assert(font >= 0x0 and font <= (0x200 - len(self.fonts)) )
        self.rom_base = base
        self.font_base = font
        # load fonts
        for n in range(len(self.fonts)):
            self.memory[n+font] = self.fonts[n]
        
        # load rom
        for i in range(len(self.rom)):
            self.memory[i+base] = self.rom[i]

        self.pc = base
        self.loaded = True

    # prints debug info in a disassembly format
    def debugger(self,curr_pc,debug_str):
        sep = "-" * 80
        print(f"I: {hex(self.I)}")
        for i,reg in enumerate(self.V):
            print(f"V{i}={hex(reg)} ", end='')
        print("")
        print(curr_pc)
        print(debug_str)
        print(sep)

    # initialized pygame display 
    def init_display(self):
        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT+1, int(1000 / 60))
        screen = pygame.display.set_mode([self.width * self.scale, self.height * self.scale])
        screen.fill(BLACK)
        pygame.display.flip()
        return screen
    
    # initializes keyboard
    # https://www.pygame.org/docs/ref/key.html
    def init_keyboard(self):
        '''
        Chip8       My Keys
        ---------   ---------
        1 2 3 C     1 2 3 4
        4 5 6 D     q w e r
        7 8 9 E     a s d f
        A 0 B F     z x c v
        '''
        # { physical key : emulated chip8 key}
        self.keybindings = {
            K_1 : 1,   K_2 : 2, K_3 : 3,   K_4 : 0xc,
            K_q : 4,   K_w : 5, K_e : 6,   K_r : 0xd,
            K_a : 7,   K_s : 8, K_d : 9,   K_f : 0xe,
            K_z : 0xa, K_x : 0, K_c : 0xb, K_v : 0xf,
            K_ESCAPE : K_ESCAPE # workaround pygame.quit() not working 
        }
        # 0 = keyup / 1 = keydown
        self.keypresses = {
            1   : 0, 2 : 0, 3   : 0, 0xc : 0,
            4   : 0, 5 : 0, 6   : 0, 0xd : 0,
            7   : 0, 8 : 0, 9   : 0, 0xe : 0,
            0xa : 0, 0 : 0, 0xb : 0, 0xf : 0
        }

    # handles pygame events
    def keyboard_handler(self):
        # iterate through every pygame event
        for event in pygame.event.get():
            # this event doesn't seem to work
            # instead make keybinding to quit
            if event.type == pygame.QUIT:
                pygame.quit()
                pygame.display.quit()
                sys.exit()
            elif event.type == pygame.USEREVENT + 1:
                self.delay_timer -= 1
            # if key is pressed
            elif event.type == pygame.KEYDOWN:
                try:
                    if self.keybindings[event.key] == K_ESCAPE:
                        pygame.quit()
                        pygame.display.quit()
                        sys.exit()
                    target = self.keybindings[event.key]
                    self.keypresses[target] = 1
                except:
                    print(f"[x] {event.key} maybe not be binded to a physical key")
            # if key is released
            elif event.type == pygame.KEYUP:
                try:
                    target = self.keybindings[event.key]
                    self.keypresses[target] = 0
                except:
                    print(f"[x] {event.key} maybe not be binded to a physical key")
        
    # draws display based on state of grid
    def display(self):
        # iterate through every element ("pixel") in grid and color pixel based on value
        # 1 = WHITE / 0 = BLACK
        for i in range(0,len(self.grid)):
            for j in range(0,len(self.grid[0])):
                cellColor = BLACK
                if self.grid[i][j] == 1:
                    cellColor = WHITE
                pygame.draw.rect(self.screen, cellColor, [j * self.scale, i * self.scale, self.scale, self.scale], 0)
        pygame.display.flip()
    
    # emulator's main loop
    def loop(self):
        assert( self.loaded == True )
        while True:
            self.parse(self.memory[self.pc:self.pc+2])
            self.clock.tick(3000)
            self.keyboard_handler()
            self.display()

    # parses and executes instructions at pc
    def parse(self,codes):
        # codes = [pc:pc+2]
        # get opcode by combining both bytes 
        opcode    = (codes[0] << 8) | codes[1]
        curr_pc   = "[{}]      0x{:04x}".format(hex(self.pc),opcode)
        debug_str = ""

        # get command from most signicate byte
        cmd = opcode >> 12      
        if cmd == 0x0:
            if opcode == 0x00e0:
                self.grid = [ [ 0 for i in range(64) ] for i in range(32) ] 
                debug_str = "Clear the screen"
            elif opcode == 0x00ee:
                self.pc = self.stack.pop()
                debug_str = "Return from subroutine"
            else:
                val = opcode & 0x0fff
                self.pc  = val
                debug_str = f"Execute at addr {hex(val)}"
        # if in 0x1NNN bucket
        elif cmd == 0x1:
            val = opcode & 0x0fff
            self.pc = val - 2
            debug_str = f"Jump to address {hex(val)}"
        # if in 0x2NNN bucket
        elif cmd == 0x2:
            val = opcode & 0x0fff
            self.stack.append(val)
            debug_str = f"Execute subroutine at address {hex(val)}"
        # if in 0x3NNN bucket
        elif cmd == 0x3:
            regx = (opcode & 0x0f00) >> 8
            nn = opcode & 0x00ff
            if self.V[regx] == nn:
                self.pc += 2
            debug_str = f"Skip following instruction if V{regx} == {hex(opcode & 0x00ff)}"
        # if in 0x4NNN bucket
        elif cmd == 0x4:
            regx = (opcode & 0x0f00) >> 8
            nn = opcode & 0x00ff
            if self.V[regx] != nn:
                self.pc += 2
            debug_str = f"Skip following instruction if V{regx} != {hex(opcode & 0x00ff)}"
        # if in 0x5NNN bucket
        elif cmd == 0x5:
            assert( (opcode & 0x000f) == 0)
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            if self.V[regx] == self.V[regy]:
                self.pc += 2
            debug_str = f"Skip following instruction if V{regx} == V{regy}"
        # if in 0x6NNN bucket
        elif cmd == 0x6:
            reg = (opcode & 0x0f00) >> 8
            val = (opcode & 0x00ff)
            self.V[reg] = val & 0xff
            debug_str = f"Store {hex(val)} in V{reg}"
        # if in 0x7NNN bucket
        elif cmd == 0x7:
            reg = (opcode & 0x0f00) >> 8
            val = (opcode & 0x00ff)
            self.V[reg] = (self.V[reg] + val) & 0xff
            debug_str = f"Add {hex(val)} to V{reg}"  
        # if in 0x8NNN bucket
        elif cmd == 0x8:
            index = opcode & 0xf
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            # Store
            if index == 0x0:
                self.V[regx] = self.V[regy]
                debug_str = f"Store V{regy} in V{regx}"
            # OR
            if index == 0x1:
                self.V[regx] |= self.V[regy]
                debug_str = f"Store V{regx} | V{regy} in V{regx}"
            # AND 
            if index == 0x2:
                self.V[regx] &= self.V[regy]
                debug_str = f"Store V{regx} & V{regy} in V{regx}"
            # XOR
            if index == 0x3:
                self.V[regx] ^= self.V[regy]
                debug_str = f"Store V{regx} ^ V{regy} in V{regx}"
            # ADD with carry
            if index == 0x4:
                self.V[regx] += self.V[regy]
                self.V[0xf] = 0
                if self.V[regx] > 0xff:
                    self.V[0xf] = 1
                    self.V[regx] = self.V[regx] & 0xff
                debug_str = f"Store V{regx} + V{regy} in V{regx} and set carry flag"
            # Check for borrow
            if index == 0x5:
                tmp = self.V[regx] - self.V[regy]
                self.V[0xf] = 1
                if tmp < 0:
                    self.V[0xf] = 0
                    self.V[regx] = abs(self.V[regx])
                debug_str = f"Check if borrow occurs in V{regx}-V{regy} and set carry flag in Vf"
            # Shift right 1 bit
            if index == 0x6:
                self.V[0xf]  = self.V[regy] & 0xf
                self.V[regx] = self.V[regy] >> 1
                debug_str = f"V{regx} = V{regy} >> 1 with least significant bit saved in Vf"
            # SUB with borrow
            if index == 0x7:
                self.V[regx] -= self.V[regy]
                self.V[0xf]   = 1
                if self.V[regx] < 0:
                    self.V[0xf]  = 0
                    self.V[regx] = abs(self.V[regx])
                debug_str = f"V{regx} -= V{regy} and set carry flag in Vf"
            # Shift left 1 bit
            if index == 0xe:
                self.V[0xf]  = self.V[regy] >> 12
                self.V[regx] = self.V[regy] << 1
                debug_str = f"V{regx} = V{regy} << 1 with most significant bit saved in Vf"
        # if in 0x9NNN bucket
        elif cmd == 0x9:
            if self.V[regx] != self.V[regy]:
                self.pc += 2
            debug_str = f"Skip following instruction if V{regx} != V{regy}"
        # if in 0xANNN bucket
        elif cmd == 0xA:
            val = (opcode & 0x0fff)
            self.I = val
            debug_str = f"Store {hex(val)} in I"
        # if in 0xBNNN bucket
        elif cmd == 0xb:
            val = opcode & 0x0fff
            self.pc = val + self.V[0]
            self.pc -= 2
            debug_str = f"Jump to address {hex(val)} + V0"
        # if in 0xCNNN bucket
        elif cmd == 0xc:
            val = opcode & 0x00ff
            r = random.randint(0,255)
            self.V[regx] = (r & val) & 0xff
            debug_str = f"Set V{regx} to random number: {hex(r)} & {hex(val)}"
        # if in 0xDNNN bucket
        elif cmd == 0xd:
            x = (opcode & 0x0f00) >> 8
            y = (opcode & 0x00f0) >> 4
            n = (opcode & 0x000f)
            sprite = self.memory[self.I:self.I+n]
            debug_str = f"Draw {n} bytes starting at ({self.V[x]},{self.V[y]}) reading from address I: {hex(self.I)}"
            bns = []
            # turn list of memory bytes into a list of lists of 8-bit binary numbers 
            for val in sprite:
                b = bin(val)[2:].zfill(8)
                bns.append( [ int(b[i],2) for i in range(len(b)) ] )
            # iterate through grid and edit "pixels" based on sprites
            regx = self.V[x] & 0xff
            regy = self.V[y] & 0xff
            for i in range(len(bns)):
                for j in range(len(bns[0])):
                    self.grid[(regy+i)][(regx+j)] ^= bns[i][j]
        # if in 0xENNN bucket
        elif cmd == 0xe:
            index = opcode & 0x00ff
            regx  = (opcode & 0x0f00) >> 8
            if index == 0x9e:
                debug_str = f"Skip following instruction if key pressed = V{regx}"
                for key in self.keypresses.keys():
                    if keypresses[key] == self.V[regx]:
                        self.pc += 2
            if index == 0xa1:
                debug_str = f"Skip following instruction if key pressed != V{regx}"
                for key in self.keypresses.keys():
                    if keypresses[key] != self.V[regx]:
                        self.pc += 2
        # if in 0xFNNN bucket
        elif cmd == 0xf:
            index = opcode & 0x00ff
            regx  = (opcode & 0x0f00) >> 8
            if index == 0x07:
                debug_str = f"Store delay timer in V{regx}"
                self.V[regx] = self.delay_timer & 0xff
            # same as keyboard_handler() but it waits to make sure it captures a KEYDOWN event
            if index == 0x0a:
                pygame.event.clear()
                while True:
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN:
                        if event.key == K_ESCAPE:
                            pygame.display.quit()
                            pygame.quit()
                            sys.exit()
                        try:
                            target = self.keybindings[event.key]
                            debug_str = f"Waited for keypress {target} and store in V{regx}"
                            self.V[regx] = target & 0xff
                            break
                        except:
                            print(f"[x] {event.key} maybe be an invalid key. Try again!")
            if index == 0x15:
                debug_str = f"Set delay timer to value in V{regx}"
                self.delay_timer = self.V[regx]
            if index == 0x18:
                debug_str = f"Set sound timer to value in V{regx}"
                self.sound_timer = self.V[regx]
            if index == 0x1e:
                debug_str = f"Set I to I + V{regx}"
                self.I += self.V[regx]
            # get font
            if index == 0x29:
                debug_str = f"set I to address of hex-digit stored in fonts {self.font_base}"
                self.I = self.font_base + (self.V[regx] * 5)
            if index == 0x33:
                # if V[3] = 0x9. dec = 009
                debug_str = f"Store BCD stored in V{regx} into memory[I], memory[I+1], memory[I+2]"
                dec = str(self.V[regx]).zill(3)
                for i in range(len(dec)):
                    self.memory[self.I + i] = int(dec[i])
            if index == 0x55:
                debug_str = f"Store values in V0 to V{regx} starting at memory[I]"
                for i in range(regx+1):
                   self.memory[self.I + i] = self.V[i] 
            if index == 0x65:
                debug_str = f"Fill registers V0 to V{regx} with values starting at memory[I]"
                for i in range(regx+1):
                    self.V[i] = self.memory[self.I + i] & 0xff
        if self.debug == True:
            self.debugger(curr_pc,debug_str)
        # advances pc
        self.pc += 2
    

