# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 2019

@author: TONG
"""
import argparse  
import os,time
from drawgcode import drawgcode
from dxftogcode import dxftogcode

if __name__ == '__main__':
    parse = argparse.ArgumentParser(description="Convert dxf to gcode and simulate physical plotter in Python")
#    parse.add_argument('keyoukewu',help='keyoukewu'，nargs='?')
    parse.add_argument('-t','--type',help='an operate type: \nc, convert dxf file to gcode file;\n s,simulate drawing gcode in Python;\n cs, both convert and simulate operation.',nargs='?')
    parse.add_argument('-f','--file',help='input file path name: \ntype is c or cs, input file should be a dxf file;\n type is s, input file should be a gcode file',nargs='?')
    
    args = parse.parse_args()
    print(args.type)
    print(args.file)
    
    shellString = "%matplotlib qt5"
    tmpCmdResult = os.system(shellString)
    print("end time:%s result: %s\n" % (time.time(),tmpCmdResult))
    
    if args.type == 'c':
        dxftogcode(args.file, args.file+".txt")
        
    if args.type == 's':
        drawgcode(args.file)
        
    if args.type == 'cs':
        dxftogcode(args.file, args.file+".txt")
        
        drawgcode(args.file+".txt")
