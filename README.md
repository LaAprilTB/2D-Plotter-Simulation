# 2D-Plotter-Simulation
2D plotter based on CNC programming concept and LEGO Mindstorms EV3

# DXF-GCODE
DXF file format is a kind of AutoCAD file format, which provide a better way for the designers to share and exchange their designs.
Gcode is a programming language based on the coordinates, which usually using in CNC programming.
This software provide a solution which able to transfer the DXF format file to Gcode instruction.

# 2D plotter simulation
After DXF to Gcode convertion, feed the Gcode to next software which able to drawing the picture out according to the gcode instructions.
At the first, there should be a plotter hardware made by Lego Mindstorms EV3, however, due to the hardwares' problem, I presented a simulation software which basically copy the way that the physical plotter do, and present the drawing using matplotlib in Python.
