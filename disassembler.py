# Chip 8 disassembler
class Disassembler():
    def __init__(self,rom_bytes):
        self.rom = rom_bytes
    
    # parse raw bytes into 2-byte opcodes
    def disassemble(self):
        opcodes = [int.from_bytes(self.rom[i:i+2],'big') for i in range(0,len(self.rom),2)]
        print(opcodes)
        while True:
            print(opcodes.pop())

# disassemble opcode to respective instruction
    def parse(self,codes):
        # maybe parse everything I need before if-tree
        opcode = (codes[0] << 8) | codes[1]
        print("[{}]      0x{:04x}".format(hex(self.pc),opcode))
        cmd = opcode >> 12      
        if cmd == 0x0:
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
        elif cmd == 0x1:
            val = opcode & 0x0fff
            self.pc = val - 2
            print(f"Jump to address {hex(val)}")
        # if in 0x2NNN bucket
        elif cmd == 0x2:
            val = opcode & 0x0fff
            self.stack.append(val)
            print(f"Execute subroutine at address {hex(val)}")
        # if in 0x3NNN bucket
        elif cmd == 0x3:
            regx = (opcode & 0x0f00) >> 8
            nn = opcode & 0x00ff
            if self.V[regx] == nn:
                self.pc += 2
            print(f"Skip following instruction if V{regx} == {hex(opcode & 0x00ff)}")
        # if in 0x4NNN bucket
        elif cmd == 0x4:
            regx = (opcode & 0x0f00) >> 8
            nn = opcode & 0x00ff
            if self.V[regx] != nn:
                self.pc += 2
            print(f"Skip following instruction if V{regx} != {hex(opcode & 0x00ff)}")
        # if in 0x5NNN bucket
        elif cmd == 0x5:
            assert( (opcode & 0x000f) == 0)
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            if self.V[regx] == self.V[regy]:
                self.pc += 2
            print(f"Skip following instruction if V{regx} == V{regy}")
        # if in 0x6NNN bucket
        elif cmd == 0x6:
            reg = (opcode & 0x0f00) >> 8
            val = (opcode & 0x00ff)
            self.V[reg] = val
            print(f"Store {hex(val)} in V{reg}")
        # if in 0x7NNN bucket
        elif cmd == 0x7:
            reg = (opcode & 0x0f00) >> 8
            val = (opcode & 0x00ff)
            self.V[reg] += val
            print(f"Add {hex(val)} to V{reg}")  
        # if in 0x8NNN bucket
        elif cmd == 0x8:
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
        elif cmd == 0x9:
            if self.V[regx] != self.V[regy]:
                self.pc += 2
            print(f"Skip following instruction if V{regx} != V{regy}")
        # if in 0xANNN bucket
        elif cmd == 0xA:
            val = (opcode & 0x0fff)
            self.I = val
            print(f"Store {hex(val)} in I")
        # if in 0xBNNN bucket
        elif cmd == 0xb:
            val = opcode & 0x0fff
            self.pc = val + self.V[0]
            self.pc -= 2
            print(f"Jump to address {hex(val)} + V0")
        # if in 0xCNNN bucket
        elif cmd == 0xc:
            val = opcode & 0x00ff
            r = random.randint(0,255)
            self.V[regx] = r & val
            print(f"Set V{regx} to random number: {hex(r)} & {hex(val)}")
        # if in 0xDNNN bucket
        elif cmd == 0xd:
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
        elif cmd == 0xe:
            index = opcode & 0x00ff
            regx  = (opcode & 0x0f00) >> 8
            if index == 0x9e:
                for key in self.keypresses.keys():
                    if keypresses[key] == self.V[regx]:
                        self.pc += 2
            if index == 0xa1:
                for key in self.keypresses.keys():
                    if keypresses[key] != self.V[regx]:
                        self.pc += 2
        # if in 0xFNNN bucket
        elif cmd == 0xf:
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
            # get font
            if index == 0x29:
                self.I = self.font_base + (self.V[regx] * 5)
            if index == 0x33:
                # if V[3] = 0x9. dec = 009
                dec = str(self.V[regx]).zill(3)
                for i in range(len(dec)):
                    self.memory[self.I + i] = int(dec[i])
            if index == 0x55:
                for i in range(regx+1):
                   self.memory[self.I + i] = self.V[i] 
            if index == 0x65:
                for i in range(regx+1):
                    self.V[i] = self.memory[self.I + i]
        self.pc += 2
        print("-" * 0x80)