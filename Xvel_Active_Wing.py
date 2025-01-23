# -*- coding: utf-8 -*-
# C:\Users\its0y\source\repos\Xvel_Active_Wing\Xvel_Active_Wing\Xvel_Active_Wing.pyproj

from webbrowser import get
import pygame
import time
import keyboard

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
        # print(f'Braking')
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
        roll_angle=-wheel_angle/15
    elif wheel_angle>0: #turning right
        roll_angle=-wheel_angle/15
    else:
        roll_angle=0
    return roll_angle

def main():

    pygame.init()

    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Wheel & Pitch Angle Display")
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    braking_time=0

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
                if braking_time>=10:
                    pitch_angle=60
                else:
                    pitch_angle=10

                screen.fill((0, 0, 0))
                wheel_text = font.render(f"Wheel angle: {wheel_angle}°", True, (255, 255, 255))
                pitch_text = font.render(f"Pitch angle: {pitch_angle}°", True, (255, 255, 255))
                roll_text = font.render(f"Wing roll angle: {roll_angle}°", True, (255, 255, 255))
                screen.blit(wheel_text, (50, 50))
                screen.blit(pitch_text, (50, 100))
                screen.blit(roll_text, (50, 150))
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

        try:
            while True:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt

                pygame.event.pump()
                wheel_angle=getWheelAngle(input_device)
                roll_angle=computeRollAngle(wheel_angle)
                braking_time=getBrakingStatus(input_device, braking_time)
                if braking_time>=10:
                    pitch_angle=60
                else:
                    pitch_angle=10

                computeRollAngle()

                screen.fill((0, 0, 0))
                wheel_text = font.render(f"Wheel angle: {wheel_angle}°", True, (255, 255, 255))
                pitch_text = font.render(f"Pitch angle: {pitch_angle}°", True, (255, 255, 255))
                roll_text = font.render(f"Wing roll angle: {roll_angle}°", True, (255, 255, 255))
                screen.blit(wheel_text, (50, 50))
                screen.blit(pitch_text, (50, 100))
                screen.blit(roll_text, (50, 150))
                pygame.display.flip()
                clock.tick(30)
                # print(f'Wheel angle: {wheel_angle}°   Pitch angle: {pitch_angle}°')
                # time.sleep(0.3)

        except KeyboardInterrupt:
            print("\nExiting program.\n")

        finally:
            pygame.quit()


if __name__ == '__main__':
    main()
