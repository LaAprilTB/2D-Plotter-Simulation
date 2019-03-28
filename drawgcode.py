#!/usr/bin/env python3
"""
Created on Wed Jan 23 2019

@author: TONG
"""
import os
import sys
import time
import numpy as np
import math, os, time
#from ev3dev.ev3 import *
import matplotlib.pyplot as plt

# state constants
ON = True
OFF = False

'''
Set up the parameters of robot plotter
'''
# the postion of motor A
Arm_Ax, Arm_Ay = 0.,0.
# the postion of motor B
Arm_Bx, Arm_By = 6.,0.
# near to pen 
nearArmLen = 16.+1.3125
# far from pen
farArmLen = 11.

penpoint = None#[3, 19.77372]

armALine = None
armBLine = None
armCLine = None
armDLine = None

armALinePlt = None
armBLinePlt = None
armCLinePlt = None
armDLinePlt = None

last_point = None
need_draw = False

'''
calculate the C,D point
set up three circle, A\B\E as the centre
C,D is the intersection of circle A and circle E,
circle B and circle D
'''
def insec(p1,r1,p2,r2):
    x = p1[0]
    y = p1[1]
    R = r1
    a = p2[0]
    b = p2[1]
    S = r2
    d = math.sqrt((abs(a-x))**2 + (abs(b-y))**2)
    if d > (R+S) or d < (abs(R-S)):
        print ("Two circles have no intersection")
        raise Exception("no intersectio")
        return
    elif d == 0 and R==S :
        print ("Two circles have same center!")
        raise Exception("same center")
        return
    else:
        A = (R**2 - S**2 + d**2) / (2 * d)
        h = math.sqrt(R**2 - A**2)
        x2 = x + A * (a-x)/d
        y2 = y + A * (b-y)/d
        x3 = round(x2 - h * (b - y) / d,2)
        y3 = round(y2 + h * (a - x) / d,2)
        x4 = round(x2 + h * (b - y) / d,2)
        y4 = round(y2 - h * (a - x) / d,2)
        print (x3, y3)
        print (x4, y4)
        c1=np.array([x3, y3])
        c2=np.array([x4, y4])
        return c1,c2


def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)


def reset_console():
    '''Resets the console to the default state'''
    print('\x1Bc', end='')


def set_cursor(state):
    '''Turn the cursor on or off'''
    if state:
        print('\x1B[?25h', end='')
    else:
        print('\x1B[?25l', end='')


def set_font(name):
    '''Sets the console font

    A full list of fonts can be found with `ls /usr/share/consolefonts`
    '''
    os.system('setfont ' + name)

def to_pos (angle):
    #0     = 14
    #-2970 = 90
    return ((angle-14.) * 197. / (90.-14.))

def to_angle (pos):
    #0     = 14
    #-2970 = 90
    return 14. + pos * (90.-14) / 197.

def calc_root(a,b,c):
    d = b**2-4*a*c
    if d < 0:
        return (0,0)
    elif d == 0:
        return ((-b+math.sqrt(d))/(2*a),(-b+math.sqrt(d))/(2*a))
    else:
        return ((-b+math.sqrt(d))/(2*a), (-b-math.sqrt(d))/(2*a))

def calc_bbo (points):
    min_x = max_x = points[0][0]
    min_y = max_y = points[0][1]
    for pt in points:
        if type(pt) is int:
            continue
        if pt[0] > max_x:
            max_x = pt[0]
        if pt[1] > max_y:
            max_y = pt[1]
        if pt[0] < min_x:
            min_x = pt[0]
        if pt[1] < min_y:
            min_y = pt[1]
    return (min_x,min_y,max_x-min_x,max_y-min_y)

'''
calculate the intersection point based on the pen position,
motor position and Arms length
call insec function to calculate the point
'''
def cal_midsec (Ptx, Pty, Motorx, Motory, nearArmLen, farArmLen):
    Pty = Pty if (not Pty == Motory) else (Pty+0.1)
    
    P1=np.array([Ptx, Pty])
    R1=nearArmLen
    P2=np.array([Motorx, Motory])
    R2=farArmLen
    C=insec(P1,R1,P2,R2)
    C1=C[0]
    C2=C[1]

    return ((C1[0],C1[1]),(C2[0],C2[1]))


def coord_to_degree (Penx, Peny):
    AngleC = 0
    AngleD = 0
    global armBLine, armALine,armCLine,armDLine,penpoint
    global armBLinePlt, armALinePlt,armCLinePlt,armDLinePlt
    try:
        ((Cx, Cy), (Cx2, Cy2)) = cal_midsec (Penx, Peny, Arm_Ax, Arm_Ay, nearArmLen, farArmLen)

        
        if Cx > Cx2:
            Cx = Cx2
            Cy = Cy2
            
        ((Dx, Dy), (Dx2, Dy2)) = cal_midsec (Penx, Peny, Arm_Bx, Arm_By, nearArmLen, farArmLen)
        (Dx, Dy) = (Dx2, Dy2) if Dx < Dx2 else (Dx, Dy)

        plt.pause(0.01)
        if armALinePlt is not None:
            armALinePlt.remove()
        if armBLinePlt is not None:
            armBLinePlt.remove()  
        if armBLinePlt is not None:
            armCLinePlt.remove()
        if armBLinePlt is not None:
            armDLinePlt.remove()
        if penpoint is not None:
            penpoint.remove()
        plt.pause(0.01)
        armALinePlt, = plt.plot([Arm_Ax, Cx], [Arm_Ay, Cy], c='y')
        armBLinePlt, = plt.plot([Arm_Bx, Dx], [Arm_By, Dy], c='y')
        armCLinePlt, = plt.plot([Cx, Penx], [Cy, Peny], c='b')
        armDLinePlt, = plt.plot([Dx, Penx], [Dy, Peny], c='b')
        plt.pause(0.01)
        
        armALine = [[Arm_Ax, Cx], [Arm_Ay, Cy]]
        armBLine = [[Arm_Bx, Dx], [Arm_By, Dy]]
        armCLine = [[Cx, Penx], [Cy, Peny]]
        armDLine = [[Dx, Penx], [Dy, Peny]]
        
        penpoint, = plt.plot(Penx, Peny, "X", c = 'b',markersize=5)
#        plt.pause(0.01)
        
        
        AngleC = 180. - 360 * math.acos((Cx-Arm_Ax)/farArmLen) / (2.*math.pi)
        AngleD =  360. * math.acos((Dx-Arm_Bx)/farArmLen) / (2.*math.pi)
    except:
        print("except-coord_to_degree!!", "Penx:", Penx, "Peny:", Peny )
        return (0.0,0.0)
    
    return (AngleC, AngleD)


def coord_to_mp (x, y):
    (AngleC, AngleD) = coord_to_degree (x, y)
    return to_pos (AngleC), -to_pos (AngleD)


def reverse_d_to_c (AngleC, AngleD):
    xA = Arm_Ax - farArmLen * math.cos((2.*math.pi) * AngleC/360.)
    yA = Arm_Ay + farArmLen * math.sin((2.*math.pi) * AngleC/360.)
    xB = Arm_Bx + farArmLen * math.cos((2.*math.pi) * AngleD/360.)
    yB = Arm_By + farArmLen * math.sin((2.*math.pi) * AngleD/360.)
    
    ((Penx, Peny), (Penx2, Peny2)) = cal_midsec (xA, yA, xB, yB, nearArmLen, nearArmLen)
    if Peny2 > Peny:
        Penx = Penx2
        Peny = Peny2
    return Penx, Peny


def mp_to_coord (pos1, pos2):
    (angleC, angleD) = (to_angle(pos1), to_angle(-pos2))
    return reverse_d_to_c (angleC, angleD)


def get_degree (Arm_Ax, Arm_Ay, Arm_Bx, Arm_By, xC, yC):
    ab2 = (Arm_Bx-Arm_Ax)*(Arm_Bx-Arm_Ax) + (Arm_By-Arm_Ay)*(Arm_By-Arm_Ay)
    bc2 = (xC-Arm_Bx)*(xC-Arm_Bx) + (yC-Arm_By)*(yC-Arm_By)
    ac2 = (xC-Arm_Ax)*(xC-Arm_Ax) + (yC-Arm_Ay)*(yC-Arm_Ay)
    try:
        cos_abc = (ab2 + bc2 - ac2) / (2*math.sqrt(ab2) * math.sqrt(bc2))
        return 180 - (360. * math.acos(cos_abc) / (2 * math.pi))
    except:
        return 180
    
class RobotArm:
    def __init__(self):
        self.pos = 0
        self.position = 0
        
    def stop(self, stop_command='coast'):
        self.stop_action = stop_command
        self.command = "stop"

    def reset_pos(self, value = 0):
        self.stop()
        
        try:
            self.position = value
        except:
            print ("impossible to fix position, attempt",iter-1,"on 10.")
        time.sleep(0.05)

    def rotate_aim(self, speed=35, stop_command='brake'):
        self.stop_action = stop_command
        self.duty_cycle_sp = int(speed)
        self.command = 'run-direct'
        
        #sim
        self.position = int(speed)

    def goto_pos(self, position, speed=35, up=0, down=0, stop_command='brake', wait=0):
        debug_print(position) 
        self.stop_action = stop_command
        
        self.duty_cycle_sp = speed
        self.position_sp = position
        self.command = 'run-to-abs-pos'

        #sim: rotate to position at one time
        self.position = position



class Printer():

    def __init__(self):
        self.arm_A = RobotArm()
        self.arm_B = RobotArm()

    def pen_up (self, wait=1):
        global need_draw
        need_draw = False
#        t.pu()
        if wait:
            time.sleep(0.1)

    def pen_down(self, wait=1):
        global need_draw
        
        need_draw = True
#        t.pd()
        if wait:
            time.sleep(0.1)


    def sp_to_coord (self,x,y,max_speed,last_x=None,last_y=None):
        posB, posA = self.arm_B.position, self.arm_A.position
        debug_print("posAB=",posA,"&&",posB)
        debug_print("posAB=",posA,"&&",posB)
#        time.sleep(1)
        myx, myy = mp_to_coord (posB, posA)
        debug_print("myxy=",myx,"&&",myy)
        debug_print("myxy=",myx,"&&",myy)
#        time.sleep(1)
        dist = math.sqrt((myx-x)*(myx-x) + (myy-y)*(myy-y))
        debug_print("dist:==",dist)
        if (last_x or last_y):
            too_far = (180-get_degree(last_x, last_y, x, y, myx, myy) >= 90)
        else:
            too_far = False
        if too_far or dist < 1:
            return 0
        
        nextx = x
        nexty = y

        next_posB, next_posA = coord_to_mp (nextx, nexty)
        debug_print("next_posAB:", next_posA, next_posB)
        

        self.arm_B.goto_pos(next_posB)
#        time.sleep(1)
        debug_print("S************")

        self.arm_A.goto_pos(next_posA)
#        time.sleep(1)
        debug_print("set-next_posA-end:", next_posA,"&&",next_posB)


#        t.goto(x, y)
        global last_point,need_draw
        if last_point is None:
            last_point = [x, y]
        if need_draw:
            plt.plot([last_point[0],x],[last_point[1], y], c='b')
        last_point = [x, y]
#        time.sleep(1)
        return 1

    def goto_point (self, x,y, last_x=None, last_y=None):
        global penpoint
        max_speed_ = 30

        penpt = [x,y]
        
        plt.pause(0.01)
        self.sp_to_coord (x,y,max_speed_,last_x,last_y)

        debug_print("goto_point-end")

    def print_graph (self, list_points):
        global penpoint, armALine, armBLine,armCLine,armDLine
        lastx = list_points[0][0]
        lasty = list_points[0][1]
        
        debug_print("list_points:",len(list_points))
        

        while (len(list_points)>0):
            debug_print("list_points:",len(list_points))
            if type(list_points[0]) is int:
                penstate = int(list_points.pop(0))
                time.sleep(0.1)
                if penstate:
                    self.pen_down()
                else:
                    self.pen_up()
                    
                return self.print_graph (list_points)
            
            (x,y) = list_points.pop(0)

            self.goto_point (x,y,lastx, lasty)
            lastx, lasty = x, y
        self.arm_A.stop()
        self.arm_B.stop()
        debug_print("print_graph-end")

    def read_gcode (self, gcfile):
        fin = open(gcfile,'r')
        list_points = []
        lastpt = None
        for line in fin:
            if line.find("(") != -1:
                continue
            
            strs = line.split()
            curpt = []
            curpt.append(float(strs[1][1:])*0.1)
            curpt.append(float(strs[2][1:])*0.1)
            if strs[0] == "G0":
                if not lastpt == None:
                    
                    list_points.append(0)
                    list_points.append(curpt)
                    list_points.append(1)
                else:
                    list_points.append(curpt)
            else:
                list_points.append(curpt)
            
            
            
            lastpt = curpt
            
        return list_points

    def fit_graph (self, points):
    

        def quad_solve (a,b,c):
            d = b**2-4*a*c
            if d < 0:
                return 0
            elif d == 0:
                return (-b+math.sqrt(d))/(2*a)
            else:
                return max((-b+math.sqrt(d))/(2*a), (-b-math.sqrt(d))/(2*a))
        def get_y_circle (circle, x):
            xC, yC, rC = circle
            a = 1
            b = -2 * yC
            c = -2*xC*x + yC**2 - rC**2 + x**2 + xC**2
            return quad_solve (a,b,c)
        def point_pos(x0, y0, d, theta):
            theta_rad = math.radians(theta)
            return x0 + d*math.cos(theta_rad), y0 + d*math.sin(theta_rad)
        def get_circles (r1, r2, xA, yA, xB, yB):
            angle_min = 100
            x, y = point_pos(xB, yB, r2, angle_min)
            left_top     = (x,y,r1)
            x,y = point_pos(xA, yA, r2, 180-angle_min)
            left_bottom  = (x,y,r1)
            return (left_top, left_bottom)
        def drange(start, stop, step):
            r = start
            while r < stop:
                yield r
                r += step

        debug_print("fit_path-begin")
        debug_print(points)
        (bbox_x, bbox_y, bbox_w, bbox_h) = calc_bbo (points)
        (left_top, left_bottom) = get_circles (farArmLen - 1, nearArmLen, Arm_Ax, Arm_Ay, Arm_Bx, Arm_By)
        min_x = max(left_top[0] - left_top[2] , left_bottom[0] - left_bottom[2] )
        best_fit, best_fit_x, best_fit_y, best_scale = 10000, 0,0,0
        mx = (Arm_Bx + Arm_Ax)/2.
        for x in drange(min_x, mx, 0.5):
            y1,y2 = get_y_circle(left_top,x)-1, get_y_circle(left_bottom,x)+1
            if (y1!=None and y2 != None):
                if (y1> y2):
                    if abs(((mx-x)*2)/(y1-y2) - (bbox_w/bbox_h)) < best_fit:
                        best_fit, best_fit_x, best_fit_y, best_scale = abs((mx-x)*2)/(y1-y2) - (bbox_w/bbox_h), x, y2, (mx-x)*2 / bbox_w

        new_points = []
        
#        best_scale = 1
        for point in points:
            if type(point) is int:
                new_points.append (point)
            else:
                new_points.append(((point[0]-bbox_x)*best_scale + best_fit_x,(point[1]-bbox_y)*best_scale + best_fit_y+10))
        debug_print("fit_path-end%d"%len(new_points))
#        print(new_points)
        return new_points

def test_print(gcodefile):
    wri = Printer()
    wri.pen_up()
    # print something to the screen of the device
    print('draw_gcode')

    # print something to the output panel in VS Code
    debug_print('draw_gcode!')
    
    plt.plot(Arm_Ax, Arm_Ay, "X", c='r')
    plt.plot(Arm_Bx, Arm_By, "X", c='r')
    penpoint1, = plt.plot(3, 28.0506, "X", c='b')
    
    # begin robot arm
    armALine1, = plt.plot([Arm_Ax,Arm_Ax],[Arm_Ay, 11], c='y')
    armBLine1, = plt.plot([Arm_Bx,Arm_Bx],[Arm_By, 11], c='y')
    armCLine1, = plt.plot([Arm_Ax, 3],[11, 28.0506], c='b')
    armDLine1, = plt.plot([Arm_Bx, 3],[11, 28.0506], c='b')
    plt.pause(1)
    penpoint1.remove()
    armALine1.remove()
    armBLine1.remove()
    armCLine1.remove()
    armDLine1.remove()
        
    list_points = wri.read_gcode(gcodefile)
    list_points = wri.fit_graph(list_points)
    wri.pen_down()
    wri.print_graph(list_points)
    
    # end robot arm
    
    armALine1, = plt.plot(armALine[0],armALine[1], c='y')
    armBLine1, = plt.plot(armBLine[0],armBLine[1], c='y')
    armCLine1, = plt.plot(armCLine[0],armCLine[1], c='b')
    armDLine1, = plt.plot(armDLine[0],armDLine[1], c='b')
    penpoint1, = plt.plot(armDLine[0][1], armDLine[1][1], "X", c='b')
    
    #wri.follow_mouse()
    wri.pen_up()

def main(gcodefile):
    '''The main function of our program'''

    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')

    # print something to the screen of the device
    print('drawing gcode')

    # print something to the output panel in VS Code
    debug_print('drawing gcode!')

    # wait a bit so you have time to look at the display before the program
    # exits
    time.sleep(1)
    test_print(gcodefile)
#    t.done()
#    time.sleep(100)

def drawgcode(gcodefile):
    main(gcodefile)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("The path of dxf is empty! ")
    
    gcodefile = sys.argv[1]
    
    main(gcodefile)
