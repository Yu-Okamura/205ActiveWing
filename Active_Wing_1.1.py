# -*- coding: utf-8 -*-
# cd C:\Users\its0y\source\repos\Xvel_Active_Wing\Xvel_Active_Wing

from webbrowser import get
import sys
import pygame
import time
import keyboard
import math
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import signal

class DeviceDisconnected(Exception):
    pass

def signal_handler(sig, frame):
    print("\nExiting program.\n")
    pygame.quit()
    plt.ioff()
    plt.close('all')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def on_close(event):
    print("\nMatplotlib window closed. \nExiting program.\n")
    pygame.quit()
    plt.ioff()
    plt.close('all')
    sys.exit(0)

def getWheelAngle(input_device):
    axis_value = input_device.get_axis(0)
    wheel_angle = int(axis_value * 450)
    return wheel_angle

def getBrakingStatus(input_device, braking_time):
    axis_value = input_device.get_axis(2)
    if axis_value < 0.9:
        braking_time+=1
    else:
        braking_time=0
    return braking_time

def getBrakingFromX(event, braking_time):
    if event.type == pygame.JOYBUTTONDOWN and event.button == 0: # X
        braking_time += 1
    elif event.type == pygame.JOYBUTTONUP and event.button == 0:
        braking_time = 0
    return braking_time

def getThrottleFromO(event, throttle_status):
    if event.type == pygame.JOYBUTTONDOWN and event.button == 1: # O
        return 1
    elif event.type == pygame.JOYBUTTONUP and event.button == 1:
        return 0

def computeRollAngle(wheel_angle):
    if wheel_angle<0: #turning left
        if wheel_angle>-150:
            wheel_angle=np.pi*wheel_angle/180
            roll_angle= 180 * ((np.pi / 12) * np.sin((6/5)*wheel_angle - (np.pi / 2)) + (np.pi/12)) / np.pi
        else:
            roll_angle=30
    elif wheel_angle>0: #turning right
        if wheel_angle<150:
            wheel_angle=np.pi*wheel_angle/180
            roll_angle= - 180 * ((np.pi / 12) * np.sin((6/5)*wheel_angle - (np.pi / 2)) + (np.pi/12)) / np.pi
        else:
            roll_angle=-30
    else:
        roll_angle=0
    return roll_angle

def displayPitchDiagram(screen, pitch_angle):
    side_length=30
    pitch_pivot = (425, 210)
    color=(255, 0, 0)
    thickness=2
    pitch_angle_rad=math.radians(pitch_angle)
    sx, sy = pitch_pivot
    x_end = sx + side_length * math.cos(pitch_angle_rad)
    y_end = sy - side_length * math.sin(pitch_angle_rad)
    pygame.draw.line(screen, color, (sx, sy), (x_end, y_end), thickness)

def diplayRollDiagram(screen, roll_angle):
    width=120
    roll_pivot = (200, 200)
    color = (0, 255, 0)
    thickness=2
    roll_angle_rad=math.radians(-roll_angle)
    cx, cy = roll_pivot
    dx = (width/2) * math.cos(roll_angle_rad)
    dy = (width/2) * math.sin(roll_angle_rad)
    x1 = cx - dx
    y1 = cy + dy
    x2 = cx + dx
    y2 = cy - dy
    pygame.draw.line(screen, color, (x1, y1), (x2, y2), thickness)

def displayMiddleMount(ax):
    line_middle_mount = np.array([[0, 0, -15], [0, 0, 0]])
    x, y, z = line_middle_mount[:, 0], line_middle_mount[:, 1], line_middle_mount[:, 2]
    ax.plot(x, y, z, color='blue', linewidth=2, label='Wing Mount')
    return 0

def displayWing(ax, roll_angle, pitch_angle):
    roll_angle_rad = np.radians(roll_angle)
    pitch_angle_rad = np.radians(pitch_angle)

    fl_y = -40 * np.cos(-roll_angle_rad)  
    fl_z = -40 * np.sin(-roll_angle_rad) 
    frontLeft = np.array([0, fl_y, fl_z])

    fr_y =  40 * np.cos(-roll_angle_rad) 
    fr_z =  40 * np.sin(-roll_angle_rad) 
    frontRight = np.array([0, fr_y, fr_z])

    cos_p = np.cos(pitch_angle_rad)
    sin_p = np.sin(pitch_angle_rad)
    depth_vec = np.array([
        10 * cos_p,  # x
        0,           # y
        10 * sin_p   # z
    ])

    rearLeft  = frontLeft  + depth_vec
    rearRight = frontRight + depth_vec
    rectangle_points = np.array([frontLeft, frontRight, rearRight, rearLeft])

    rect_poly = Poly3DCollection(
        [rectangle_points],
        facecolors='blue',
        alpha=0.5,  
        edgecolor='blue',
        label=f'Wing (roll={round(roll_angle, 2)}°, pitch={pitch_angle}°)'
    )
    ax.add_collection3d(rect_poly)

    rear_vec = rearRight - rearLeft
    rear_length = np.linalg.norm(rear_vec)

    rear_dir = rear_vec / rear_length

    paramA = 25.0 / rear_length
    paramB = 1.0 - 25.0 / rear_length

    dotLeft  = rearLeft + paramA * rear_vec 
    dotRight = rearLeft + paramB * rear_vec

    ax.scatter([dotLeft[0]],  [dotLeft[1]],  [dotLeft[2]],
               color='red', s=15, marker='o')
    ax.scatter([dotRight[0]], [dotRight[1]], [dotRight[2]],
               color='red', s=15, marker='o')

    endLeft  = np.array([5, -15, -25])
    endRight = np.array([5,  15, -25])

    ax.plot([dotLeft[0], endLeft[0]],
            [dotLeft[1], endLeft[1]],
            [dotLeft[2], endLeft[2]],
            color='red', linewidth=2)

    ax.plot([dotRight[0], endRight[0]],
            [dotRight[1], endRight[1]],
            [dotRight[2], endRight[2]],
            color='red', linewidth=2)

    lengthLeft  = np.linalg.norm(endLeft  - dotLeft)
    lengthRight = np.linalg.norm(endRight - dotRight)
    
    midLeft  = (dotLeft  + endLeft ) / 2.0
    midRight = (dotRight + endRight) / 2.0
    
    ax.text(
        midLeft[0], midLeft[1], midLeft[2],
        f"{lengthLeft:.2f}",
        color='red'
    )
    ax.text(
        midRight[0], midRight[1], midRight[2],
        f"{lengthRight:.2f}",
        color='red'
    )

    return 0
        
     
def main():

    pygame.init()
    pygame.joystick.init()

    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    fig.canvas.mpl_connect('close_event', on_close)

    braking_time=0
    throttle_status = 0
    pitch_angle=0

    input_device = pygame.joystick.Joystick(0)
    input_device.init()
    print(f'{input_device.get_name()} detecteed.')
    # initial_axis_value = input_device.get_axis(2)

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt
                
            pygame.event.pump()
            wheel_angle=getWheelAngle(input_device)
            roll_angle=computeRollAngle(wheel_angle)
            # braking_time=getBrakingStatus(input_device, braking_time)
            braking_time = getBrakingFromX(event, braking_time)
            throttle_status = getThrottleFromO(event, throttle_status)

            if braking_time>=5:
                if pitch_angle>=60:
                    pitch_angle=60
                else:
                    pitch_angle+=15

            else:
                if pitch_angle>=30:
                    pitch_angle-=15
                else:
                    pitch_angle=15

            ax.clear()

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_xlim(-50, 50)
            ax.set_ylim(-50, 50)
            ax.set_zlim(-50, 50)

            displayMiddleMount(ax)
            displayWing(ax, roll_angle, pitch_angle)

            ax.legend()
            plt.draw()

            # clock.tick(30)
            plt.pause(0.05)

    except KeyboardInterrupt:
        print("\nExiting program.\n")

    finally:
        pygame.quit()
        plt.ioff()
        plt.close('all')
        sys.exit(0)

if __name__ == '__main__':
    main()
