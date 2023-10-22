from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput

# Global variables for calibration
Slope = 1.0  # Replace with your calibration values
Offset = 0.0  # Replace with your calibration values

def onVoltageRatioChange(self, voltageRatio):
    # Convert voltage ratio to Newtons using the calibration equation
    force = voltageRatio * Slope + Offset
    print("Force (Newtons): {:.2f}".format(force))

def main():
    # Create your Phidget channels
    voltageRatioInput0 = VoltageRatioInput()

    # Set addressing parameters to specify which channel to open (if any)

    # Assign any event handlers you need before calling open so that no events are missed.
    voltageRatioInput0.setOnVoltageRatioChangeHandler(onVoltageRatioChange)

    # Open your Phidgets and wait for attachment
    voltageRatioInput0.openWaitForAttachment(5000)

    # Do stuff with your Phidgets here or in your event handlers.

    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

    # Close your Phidgets once the program is done.
    voltageRatioInput0.close()

if __name__ == "__main__":
    main()
