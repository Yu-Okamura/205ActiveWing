# -*- coding: utf-8 -*-
# C:\Users\its0y\source\repos\Xvel_Active_Wing\Xvel_Active_Wing\Xvel_Active_Wing.pyproj

from webbrowser import get
import pygame
import time


def getWheelAngle(input_device):
    axis_value = input_device.get_axis(0)
    wheel_angle = int(axis_value * 450)
    return wheel_angle

def getBrakingStatus(input_device, braking_time):
    axis_value = input_device.get_axis(2)
    if axis_value < 0.9:
        # print(f'Braking')
        braking_time+=1
    else:
        braking_time=0
    return braking_time

def computeRollAngle():
    return 0

def main():

    pygame.init()
    braking_time=0

    if pygame.joystick.get_count() == 0:
        print('\nNo wheel detectred. Exiting program.\n')
        exit()

    else:
        input_device = pygame.joystick.Joystick(0)
        input_device.init()
        print(f'{input_device.get_name()} detecterd.')

        try:
            while True:
                pygame.event.pump()
                wheel_angle=getWheelAngle(input_device)
                braking_time=getBrakingStatus(input_device, braking_time)
                if braking_time>=2:
                    pitch_angle=60
                else:
                    pitch_angle=5

                computeRollAngle()

                print(f'Wheel angle: {wheel_angle}°   Pitch angle: {pitch_angle}°')
                time.sleep(10)

        except KeyboardInterrupt:
            print("\nExiting program.\n")

        finally:
            pygame.quit()


if __name__ == '__main__':
    main()