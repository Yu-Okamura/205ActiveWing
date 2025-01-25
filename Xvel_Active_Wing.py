# -*- coding: utf-8 -*-
# cd C:\Users\its0y\source\repos\Xvel_Active_Wing\Xvel_Active_Wing

from webbrowser import get
import pygame
import time
import keyboard
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def getWheelAngle(input_device):
    axis_value = input_device.get_axis(0)
    wheel_angle = int(axis_value * 450)
    return wheel_angle

def getWheelAngleForArrow(wheel_angle):
    if keyboard.is_pressed('left'):
        if wheel_angle>=-360:
            wheel_angle-=90
        else:
            wheel_angle=-450
    elif keyboard.is_pressed('right'):
        if wheel_angle<=360:
            wheel_angle+=90
        else:
            wheel_angle=450
    elif wheel_angle>=45:
        wheel_angle-=45
    elif wheel_angle<=-45:
        wheel_angle+=45
    else:
        wheel_angle=0
    return wheel_angle

def getBrakingStatus(input_device, braking_time):
    axis_value = input_device.get_axis(2)
    if axis_value < 0.9:
        braking_time+=1
    else:
        braking_time=0
    return braking_time

def getBrakingStatusForArrow(braking_time):
    if keyboard.is_pressed('down'):
        braking_time+=1
    else:
        braking_time=0
    return braking_time

def computeRollAngle(wheel_angle):
    if wheel_angle<0: #turning left
        if wheel_angle>-150:
            roll_angle=-wheel_angle/5
        else:
            roll_angle=30
    elif wheel_angle>0: #turning right
        if wheel_angle<150:
            roll_angle=-wheel_angle/5
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
    # display middle mount
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
        label=f'Wing (roll={roll_angle}°, pitch={pitch_angle}°)'
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

    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Roll and Pitch Angle Display")
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    braking_time=0
    pitch_angle=0

    if pygame.joystick.get_count() == 0:
        print('\nNo wheel detectred. Exiting program. \nUse \"down-arrow\" for braking input and \"side-arrow\" for steering input.')
        wheel_angle=0
        try:
            while True:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt

                wheel_angle=getWheelAngleForArrow(wheel_angle)
                roll_angle=computeRollAngle(wheel_angle)
                braking_time=getBrakingStatusForArrow(braking_time)

                if braking_time>=15:
                    if pitch_angle>=60:
                        pitch_angle=60
                    else:
                        pitch_angle+=10
                    braking_status=True
                else:
                    pitch_angle=10
                    braking_status=False

                screen.fill((0, 0, 0))
                
                wheel_text = font.render(f"Wheel angle: {wheel_angle}°", True, (255, 255, 255))
                roll_text = font.render(f"Roll angle: {round(roll_angle, 2)}°", True, (255, 255, 255))
                braking_text = font.render(f"Braking: {braking_status}", True, (255, 255, 255))
                pitch_text = font.render(f"Pitch angle: {pitch_angle}°", True, (255, 255, 255))
                
                screen.blit(wheel_text, (100, 50))
                screen.blit(roll_text, (100, 100))
                screen.blit(braking_text, (350, 50))
                screen.blit(pitch_text, (350, 100))

                displayPitchDiagram(screen, pitch_angle)
                diplayRollDiagram(screen, roll_angle)

                pygame.display.flip()
                clock.tick(30)
                # print(f'Wheel angle: {wheel_angle}°   Pitch angle: {pitch_angle}°')
                # time.sleep(0.3)

        except KeyboardInterrupt:
            print("\nExiting program.\n")

        finally:
            pygame.quit()

    else:
        input_device = pygame.joystick.Joystick(0)
        input_device.init()
        print(f'{input_device.get_name()} detecterd.')
        initial_axis_value = input_device.get_axis(2)

        try:
            while True:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt

                pygame.event.pump()
                wheel_angle=getWheelAngle(input_device)
                roll_angle=computeRollAngle(wheel_angle)
                braking_time=getBrakingStatus(input_device, braking_time)

                if braking_time>=5:
                    if pitch_angle>=60:
                        pitch_angle=60
                    else:
                        pitch_angle+=15
                    braking_status=True
                else:
                    if pitch_angle>=30:
                        pitch_angle-=15
                    else:
                        pitch_angle=15
                    braking_status=False

                screen.fill((0, 0, 0))

                wheel_text = font.render(f"Wheel angle: {wheel_angle}°", True, (255, 255, 255))
                roll_text = font.render(f"Roll angle: {round(roll_angle, 2)}°", True, (255, 255, 255))
                braking_text = font.render(f"Braking: {braking_status}", True, (255, 255, 255))
                pitch_text = font.render(f"Pitch angle: {pitch_angle}°", True, (255, 255, 255))
                
                screen.blit(wheel_text, (100, 50))
                screen.blit(roll_text, (100, 100))
                screen.blit(braking_text, (350, 50))
                screen.blit(pitch_text, (350, 100))
                

                displayPitchDiagram(screen, pitch_angle)
                diplayRollDiagram(screen, roll_angle)

                pygame.display.flip()


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


if __name__ == '__main__':
    main()
