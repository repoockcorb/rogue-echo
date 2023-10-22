import odrive
from odrive.enums import *
import time
import openpyxl

# Find a connected ODrive (this will block until you connect one)
odrive = odrive.find_any()

# Clear Odrive S1 Errors if any
odrive.clear_errors()

#load my_config.json
# odrive.load_configuration("my_config.json")

# Ask to Calibrate motor and wait for it to finish
while True:
    response = input("Do you want to run calibration Y/n?")
    if response == "Y" or response == "y":
        print("starting calibration...")
        odrive.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
        while odrive.axis0.current_state != AXIS_STATE_IDLE:
            time.sleep(0.1)
        print("Calibration Complete")
        break
    elif response == "n" or response == "N":
        print("skipping calibration")
        break
    else:
        print("Invalid input. Please enter Y or n")

# Configure motor 
odrive.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
odrive.axis0.controller.config.vel_ramp_rate = 0.5
odrive.axis0.controller.config.vel_limit = 10
odrive.axis0.controller.config.vel_gain = 0.167
odrive.axis0.controller.config.vel_integrator_gain = 0.333
odrive.axis0.controller.config.input_mode = InputMode.VEL_RAMP
# odrive.axis0.controller.config.input_mode = INPUT_MODE_PASSTHROUGH  
odrive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

# Make sure the initial velocity is set to 0
odrive.axis0.controller.input_vel = 0 # target velocity in counts/s

# Create New Excel workbook and sheet
wb = openpyxl.Workbook()
sheet = wb.active
sheet.title = "Motor RPM vs Power"
sheet["A1"] = "RPM"
sheet["B1"] = "Power (W)"

# rpm_set_points = [120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200]
rpm_set_points = [60, 120, 240, 320]
# rpm_set_points = [128]

input("Press Enter to continue...")

# Run motor at set points and record power
while True:
    response = input("Are you ready to start Y/n?")
    if response == "Y" or response == "y":
        for rpm in rpm_set_points:
            print("Starting...")
            time.sleep(0.1)
            odrive.axis0.controller.input_vel = rpm/60 # Divide by 60 to convert from rpm to rps
            print("Motor Setpoint: " + str(rpm) + "rpm")
            print("waiting for motor to reach setpoint")
            time.sleep(30)
            print("Target Setpoint Reached")
            time.sleep(0.1)
            power = odrive.axis0.motor.electrical_power
            print("Motor power:", power)
            sheet.append([rpm, power])
            time.sleep(0.1)
        # Save Excel workbook
        print("Saving Excel workbook...")
        wb.save("RPM vs Power Test 2.xlsx")
        time.sleep(5)
        # Set Odrive State to Idle
        odrive.axis0.requested_state = AXIS_STATE_IDLE
        print("Done!")
        break
    elif response == "n" or response == "N":
        print("Aborting...")
        # Set Odrive State to Idle
        odrive.axis0.requested_state = AXIS_STATE_IDLE
        break
    else:
        print("Invalid input. Please enter Y or n")

# Deinit motor and set to 0 rpm
odrive.axis0.controller.input_vel = 0 # target velocity in counts/s





