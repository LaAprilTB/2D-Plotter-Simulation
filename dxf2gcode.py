# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 2019

@author: TONG
"""

import ezdxf
import sys
import string


def conv_line(e, value):
    
    gcode = "G0 "+"X"+str(e.dxf.start[0])+" Y"+str(e.dxf.start[1])+"\n"
    gcode += "G1 "+"X"+str(e.dxf.end[0])+" Y"+str(e.dxf.end[1])+"\n"

    return gcode


def conv_polyline(e, value):

    pts = e.get_points()  # Get every points in the polyline
    gcode = ""

    for i, pt in enumerate(pts):
        value.update({"X": pt[0], "Y": pt[1]})
        if i == 0:
            first_pt = (pt[0],pt[1])
            #print(first_pt)
            gcode = string.Template(
                'G0 X$X Y$Y\n').substitute(value)
        else:
            gcode += string.Template("G1 X$X Y$Y  F$Vel\n").substitute(value)


    #Check if the polyline closed
    if e.closed:
        value.update({"X": first_pt[0], "Y": first_pt[1]})
        gcode += string.Template("G01 X$X Y$Y  F$Vel\n").substitute(value)

    return gcode


def dxftogcode( infilename, outfilename):
    input_filename = infilename
    output_filename = outfilename
    n_layer = 5

    value = {"Vel": 1000}

    # Read DXF Objects and Generate GCode
    dwg = ezdxf.readfile(input_filename)
    modelspace = dwg.modelspace()

    # Append GCode header
    gcode = ""
    # Multiple Layers
    for layer in range(0, n_layer):
        #value.update({"Q1": round(value["Q1"]+incr1, 2), "Q2": round(value["Q2"]+incr2, 2)})
        gbody = "(Layer {})\n".format(layer+1)
        for e in modelspace:
            if e.dxftype() == 'LINE':
                gbody += conv_line(e, value)

            if e.dxftype() == 'LWPOLYLINE':
                gbody += conv_polyline(e, value)
        gcode += gbody

    # Append GCode Footer
    print(gcode)

    # Write to File
    with open(output_filename, 'w') as f:
        f.write(gcode)

if __name__ == "__main__":
    if len(sys.argv) < 3:
            raise Exception("The path of dxf is empty! ")
    
    dxffile = sys.argv[1]
    outfile = sys.argv[2]
    dxftogcode(dxffile, outfile)
