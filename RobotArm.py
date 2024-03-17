import pyfirmata
import time


import threading


class RobotArm(object):
    base_angle = 90.0
    shoulder_angle = 45.0
    elbow_angle = 120.0
    wrist_roll_angle = 120.0
    wrist_pitch_angle = 90.0
    gripper_angle = 45.0

    board = None
    base = None
    shoulder = None
    elbow = None
    wrist_roll = None
    wrist_pitch = None
    gripper = None

    def __init__(self):
        print("in __init__")
        self.board = pyfirmata.Arduino('COM8')

        self.board.servo_config(3, angle=self.base_angle)
        self.base = self.board.get_pin('d:3:s')
        self.base.write(self.base_angle)

        self.board.servo_config(5, angle=self.shoulder_angle)
        self.shoulder = self.board.get_pin('d:11:s')
        self.shoulder.write(self.shoulder_angle)

        self.board.servo_config(6, angle=self.elbow_angle)
        self.elbow = self.board.get_pin('d:10:s')
        self.elbow.write(self.elbow_angle)

        self.board.servo_config(9, angle=self.wrist_roll_angle)
        self.wrist_roll = self.board.get_pin('d:9:s')
        self.wrist_roll.write(self.wrist_roll_angle)

        self.board.servo_config(10, angle=self.wrist_pitch_angle)
        self.wrist_pitch = self.board.get_pin('d:6:s')
        self.wrist_pitch.write(90.0)

        self.board.servo_config(10, angle=self.gripper_angle)
        self.gripper = self.board.get_pin('d:5:s')
        self.gripper.write(90.0)

    def __del__(self):
        print("in __del__")
        self.goto(90, 45, 120, 120, 90, 45)
        self.board.exit()

    def sweep_base(self, base_desired):
        base_desired = max(base_desired, 0.0)
        base_desired = min(base_desired, 180.0)
        while abs(self.base_angle - base_desired) > 0.1:
            if self.base_angle <= base_desired:
                self.base_angle = self.base_angle + 1.0
            elif self.base_angle > base_desired:
                self.base_angle = self.base_angle - 1.0

            self.base.write(self.base_angle)
            time.sleep(0.015)

    def sweep_shoulder(self, shoulder_desired):
        shoulder_desired = max(shoulder_desired, 0.0)
        shoulder_desired = min(shoulder_desired, 180.0)
        while abs(self.shoulder_angle - shoulder_desired) > 0.1:
            if self.shoulder_angle <= shoulder_desired:
                self.shoulder_angle = self.shoulder_angle + 1.0
            elif self.shoulder_angle > shoulder_desired:
                self.shoulder_angle = self.shoulder_angle - 1.0

            self.shoulder.write(self.shoulder_angle)
            time.sleep(0.015)

    def sweep_elbow(self, elbow_desired):
        elbow_desired = max(elbow_desired, 0.0)
        elbow_desired = min(elbow_desired, 180.0)
        while abs(self.elbow_angle - elbow_desired) > 0.1:
            if self.elbow_angle <= elbow_desired:
                self.elbow_angle = self.elbow_angle + 1.0
            elif self.elbow_angle > elbow_desired:
                self.elbow_angle = self.elbow_angle - 1.0

            self.elbow.write(self.elbow_angle)
            time.sleep(0.015)

    def sweep_wrist_roll(self, wrist_roll_desired):
        wrist_roll_desired = max(wrist_roll_desired, 0.0)
        wrist_roll_desired = min(wrist_roll_desired, 90.0)
        while abs(self.wrist_roll_angle - wrist_roll_desired) > 0.1:
            if self.wrist_roll_angle <= wrist_roll_desired:
                self.wrist_roll_angle = self.wrist_roll_angle + 1.0
            elif self.wrist_roll_angle > wrist_roll_desired:
                self.wrist_roll_angle = self.wrist_roll_angle - 1.0

            self.wrist_roll.write(self.wrist_roll_angle)
            time.sleep(0.015)

    def sweep_wrist_pitch(self, wrist_pitch_desired):
        wrist_pitch_desired = max(wrist_pitch_desired, 0.0)
        wrist_pitch_desired = min(wrist_pitch_desired, 90.0)
        while abs(self.wrist_pitch_angle - wrist_pitch_desired) > 0.1:
            if self.wrist_pitch_angle <= wrist_pitch_desired:
                self.wrist_pitch_angle = self.wrist_pitch_angle + 1.0
            elif self.wrist_pitch_angle > wrist_pitch_desired:
                self.wrist_pitch_angle = self.wrist_pitch_angle - 1.0

            self.wrist_pitch.write(self.wrist_pitch_angle)
            time.sleep(0.015)

    def sweep_gripper(self, gripper_desired):
        gripper_desired = max(gripper_desired, 0.0)
        gripper_desired = min(gripper_desired, 90.0)
        while abs(self.gripper_angle - gripper_desired) > 0.1:
            if self.gripper_angle <= gripper_desired:
                self.gripper_angle = self.gripper_angle + 1.0
            elif self.gripper_angle > gripper_desired:
                self.gripper_angle = self.gripper_angle - 1.0

            self.wrist_roll.write(self.wrist_roll_angle)
            time.sleep(0.015)

    def home(self):
        self.sweep_base(90)
        self.sweep_shoulder(45)
        self.sweep_elbow(120)
        # self.sweep_wrist_roll(90)
        self.sweep_wrist_pitch(90)

    def goto(self, base_desired, shoulder_desired, elbow_desired, wrist_roll_desired, wrist_pitch_desired,
             gripper_desired):
        self.sweep_base(base_desired)
        self.sweep_shoulder(shoulder_desired)
        self.sweep_elbow(elbow_desired)
        self.sweep_wrist_roll(wrist_roll_desired)
        self.sweep_wrist_pitch(wrist_pitch_desired)
        self.sweep_gripper(gripper_desired)

        print(str(self.base_angle) + "," + str(self.shoulder_angle) + "," + str(self.elbow_angle) + ', ' +
              str(self.wrist_roll_angle) + ', ' + str(self.wrist_pitch_angle) + ', ' + str(self.gripper_angle))
        time.sleep(0.2)

    def grip(self):
        self.sweep_gripper(60.0)
        self.sweep_gripper(0.0)