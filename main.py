import argparse
import hexdump
import pygame
import time

#import instructions
from emulator import Emulator

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
def parse(opcode):
    print("0x{:04x}".format(opcode),end=' ')
    if opcode >> 12 == 0x0:
        if opcode == 0x00e0:
            print("Clear the screen")
        elif opcode == 0x00ee:
            print("Return from subroutine")
        else:
            print(f"Execute at addr {hex(opcode & 0x0fff)}")
    # if in 0x1NNN bucket
    elif opcode >> 12 == 0x1:
        print(f"Jump to address {hex(opcode & 0x0fff)}")
    # if in 0x2NNN bucket
    elif opcode >> 12 == 0x2:
        print(f"Execute subroutine at address {hex(opcode & 0x0fff)}")
    # if in 0x3NNN bucket
    elif opcode >> 12 == 0x3:
        reg = (opcode & 0x0f00) >> 8
        print(f"Skip following instruction if V{reg} == {hex(opcode & 0x00ff)}")
    # if in 0x4NNN bucket
    elif opcode >> 12 == 0x4:
        reg = (opcode & 0x0f00) >> 8
        print(f"Skip following instruction if V{reg} != {hex(opcode & 0x00ff)}")
    # if in 0x5NNN bucket
    elif opcode >> 12 == 0x5:
        # assert (opcode & 0xf == 0)
        regx = (opcode & 0x0f00) >> 8
        regy = (opcode & 0x00f0) >> 4
        print(f"Skip following instruction if V{regx} == V{regy}")
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
    # if in 0x8NNN bucket
    elif opcode >> 12 == 0x8:
        # Store
        if opcode & 0xf == 0x0:
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            print(f"Store V{regy} in V{regx}")
        # OR
        if opcode & 0xf == 0x1:
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            print(f"Store V{regx} | V{regy} in V{regx}")
        # AND 
        if opcode & 0xf == 0x2:
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            print(f"Store V{regx} & V{regy} in V{regx}")
        # XOR
        if opcode & 0xf == 0x3:
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            print(f"Store V{regx} ^ V{regy} in V{regx}")
        
        if opcode & 0xf == 0x4:
            regx = (opcode & 0x0f00) >> 8
            regy = (opcode & 0x00f0) >> 4
            print(f"Store V{regx} & V{regy} in V{regx}")

    # if in 0x9NNN bucket
    elif opcode >> 12 == 0x9:
        print("")
    # if in 0xANNN bucket
    elif opcode >> 12 == 0xA:
        val = opcode & 0x0fff
        print(f"Store {hex(val)} in I register")
    # if in 0xBNNN bucket
    elif opcode >> 12 == 0xB:
        print("")
    # if in 0xCNNN bucket
    elif opcode >> 12 == 0xC:
        print("")
    # if in 0xDNNN bucket
    elif opcode >> 12 == 0xD:
        regx = opcode & 0x0f00
        regy = opcode & 0x00f0
        regn = opcode & 0x000f
        print(f"Draw {regn} bytes starting at [I] @ position (V{regx},V{regy})")
    # if in 0xENNN bucket
    elif opcode >> 12 == 0xE:
        print("")
    # if in 0xFNNN bucket
    elif opcode >> 12 == 0xF:
        print("")

    else:
        print("Undefined opcode")


def main():
    rom = "ch8s\\IBMLogo.ch8"
    with open(rom,"rb") as f:
        data = f.read()
    # emulator currently loops endlessly displaying random bits on screen
    emulator = Emulator(data)
    emulator.loop()
    d = Disassembler(data)
    #d.disassemble()


    
    
main()