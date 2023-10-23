from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
import pandas as pd
import numpy as np
import time
import os

# Initialize an empty DataFrame for data storage
data = pd.DataFrame(columns=['Force (Kilograms)', 'Timestamp'])

# Known forces in Newtons and corresponding voltage ratios
known_forces = [117.6798, 833.56525]  # List of known forces in Newtons
voltage_ratios = [0.00041301269, 0.002570771612]  # List of corresponding voltage ratios

# Perform linear regression to calculate the slope and intercept (offset)
slope, offset = np.polyfit(voltage_ratios, known_forces, 1)

def newtons_to_kilograms(newtons):
    # Conversion factor
    kg_per_newton = 0.10197162129779283
    return newtons * kg_per_newton

def onVoltageRatioChange(self, voltageRatio):
    # Convert voltage ratio to Newtons using the calibration equation
    force_newtons = voltageRatio * slope + offset
    force_kilograms = newtons_to_kilograms(force_newtons)
    print("Force (Kilograms): {:.2f} kg".format(force_kilograms))
    log_data(force_kilograms)

def log_data(force_kilograms):
    global data  # Use the globally defined DataFrame

    # Create a new DataFrame with the data
    new_data = pd.DataFrame({'Force (Kilograms)': [force_kilograms], 'Timestamp': [time.strftime('%Y-%m-%d %H:%M:%S')]})

    # Concatenate the new DataFrame with the existing data
    data = pd.concat([data, new_data], ignore_index=True)

    # Save the DataFrame to the Excel file
    data.to_excel('force data.xlsx', index=False)

def main():
    # Create your Phidget channel
    voltageRatioInput1 = VoltageRatioInput()  # Use input 1

    # Set addressing parameters to specify which channel to open (in this case, input 1)
    voltageRatioInput1.setChannel(1)

    # Assign the event handler to log and export data
    voltageRatioInput1.setOnVoltageRatioChangeHandler(onVoltageRatioChange)

    # Open your Phidget and wait for attachment
    voltageRatioInput1.openWaitForAttachment(5000)

    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

    # Close your Phidget once the program is done
    voltageRatioInput1.close()

if __name__ == "__main__":
    main()




# from Phidget22.Phidget import *
# from Phidget22.Devices.VoltageRatioInput import *
# import time

# #Declare any event handlers here. These will be called every time the associated event occurs.

# def onVoltageRatioChange(self, voltageRatio):
# 	print("VoltageRatio: " + str(voltageRatio))

# def main():
# 	#Create your Phidget channels
# 	voltageRatioInput1 = VoltageRatioInput()

# 	#Set addressing parameters to specify which channel to open (if any)
# 	voltageRatioInput1.setChannel(1)

# 	#Assign any event handlers you need before calling open so that no events are missed.
# 	voltageRatioInput1.setOnVoltageRatioChangeHandler(onVoltageRatioChange)

# 	#Open your Phidgets and wait for attachment
# 	voltageRatioInput1.openWaitForAttachment(5000)

# 	#Do stuff with your Phidgets here or in your event handlers.

# 	try:
# 		input("Press Enter to Stop\n")
# 	except (Exception, KeyboardInterrupt):
# 		pass

# 	#Close your Phidgets once the program is done.
# 	voltageRatioInput1.close()

# main()

# from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
# import numpy as np

# # Known forces in Newtons and corresponding voltage ratios
# known_forces = [117.6798, 833.56525]  # List of known forces in Newtons
# voltage_ratios = [0.00041301269, 0.002570771612]  # List of corresponding voltage ratios

# # Perform linear regression to calculate the slope and intercept (offset)
# slope, offset = np.polyfit(voltage_ratios, known_forces, 1)

# def onVoltageRatioChange(self, voltageRatio):
#     # Convert voltage ratio to Newtons using the calibration equation
#     force = voltageRatio * slope + offset
#     print("Force (Newtons): {:.2f}".format(force))

# def main():
#     # Create your Phidget channels
#     voltageRatioInput1 = VoltageRatioInput()  # Use input 1

#     # Set addressing parameters to specify which channel to open (in this case, input 1)
#     voltageRatioInput1.setChannel(1)

#     # Assign any event handlers you need before calling open so that no events are missed.
#     voltageRatioInput1.setOnVoltageRatioChangeHandler(onVoltageRatioChange)

#     # Open your Phidgets and wait for attachment
#     voltageRatioInput1.openWaitForAttachment(5000)

#     # Do stuff with your Phidgets here or in your event handlers.

#     try:
#         input("Press Enter to Stop\n")
#     except (Exception, KeyboardInterrupt):
#         pass

#     # Close your Phidgets once the program is done.
#     voltageRatioInput1.close()

# if __name__ == "__main__":
#     main()


# from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
# import numpy as np


# # Known forces and corresponding voltage ratios
# # known_forces = [12, 85]  # List of known forces
# known_forces = [117.6798, 833.56525]  # List of known forces
# voltage_ratios = [0.00041301269, 0.002570771612]  # List of corresponding voltage ratios

# # Perform linear regression to calculate the slope and intercept (offset)
# slope, offset = np.polyfit(known_forces, voltage_ratios, 1)


# def onVoltageRatioChange(self, voltageRatio):
#     # Convert voltage ratio to Newtons using the calibration equation
#     force = voltageRatio * slope + offset
#     print("Force (Newtons): {:.2f}".format(force))

# def main():
#     # Create your Phidget channels
#     voltageRatioInput1 = VoltageRatioInput()  # Use input 1

#     # Set addressing parameters to specify which channel to open (in this case, input 1)
#     voltageRatioInput1.setChannel(1)

#     # Assign any event handlers you need before calling open so that no events are missed.
#     voltageRatioInput1.setOnVoltageRatioChangeHandler(onVoltageRatioChange)

#     # Open your Phidgets and wait for attachment
#     voltageRatioInput1.openWaitForAttachment(5000)

#     # Do stuff with your Phidgets here or in your event handlers.

#     try:
#         input("Press Enter to Stop\n")
#     except (Exception, KeyboardInterrupt):
#         pass

#     # Close your Phidgets once the program is done.
#     voltageRatioInput1.close()

# if __name__ == "__main__":
#     main()
