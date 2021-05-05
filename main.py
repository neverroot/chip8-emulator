import argparse

from emulator import Emulator


if __name__ == '__main__':
    # argument parsing
    parser = argparse.ArgumentParser(description="Chip 8 emulator")
    parser.add_argument("rom",help="path to .ch8 file")
    parser.add_argument("--rom_base",type=int,default=0x200,help="base address for rom to be loaded into")
    parser.add_argument("--font_base",type=int,default=0x0,help="base address for font to be loaded into")
    parser.add_argument("-d",action='store_true',default=False,help="debug mode")
    args = parser.parse_args()

    with open(args.rom,"rb") as f:
        data = f.read()
    emulator = Emulator(data,debug=args.d)
    emulator.load(base=args.rom_base,font=args.font_base)
    emulator.loop()