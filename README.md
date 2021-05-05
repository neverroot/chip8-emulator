# chip8-emulator

Chip 8 Emulator written in pure Python 3

NOTE: I'm not going to implement audio, mainly because I don't care much for the beeps

Default settings = base address of rom = 0x200, base address of font = 0x50, no debug mode

To use quickly use emulaator with default settings:

`python3 main.py [path to rom]`

To use emulator with debug mode on:

`python3 main.py [path to rom] -d`

To use emulator with custom base addresses for font and rom:

`python3 main.py [path to rom] --rom_base 592 --font_base 100`


TODO:

- Add disassembler to just print out the disassembly of any .ch8 file
- Add option to force emulator to use undocumented instructions or the "ambiguous instructions" noted by Tobias V. Langhoff (4th source)
- Maybe add time travel debugging???

Resources used: 
- http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#dispcoords
- https://github.com/mattmikolay/chip-8/wiki/CHIP%E2%80%908-Technical-Reference
- https://github.com/mattmikolay/chip-8/wiki/CHIP%E2%80%908-Instruction-Set
- https://tobiasvl.github.io/blog/write-a-chip-8-emulator/
