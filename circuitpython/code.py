import time
import board
import digitalio

# Initialize variables
revolutions = 0
last_button_state = True  # Set the initial state to True (unpressed)
last_time = time.monotonic()
update_interval = 0.0001  # Update interval in seconds (10 ms)

# Define the button pin as an interrupt source
button = digitalio.DigitalInOut(board.GP10)
button.switch_to_input(pull=digitalio.Pull.UP)

while True:
    current_time = time.monotonic()
    if button.value == 1:
        #print("button pressed")
        while True:
            if current_time - last_time >= update_interval:
                rev_per_sec = revolutions / (current_time - last_time)
                revolutions = 0  # Reset the count

                print("Revolutions per second (rpm):", (rev_per_sec/7)*60)
                last_time = current_time
            if button.value == 0:
                #print("waiting for release")
                revolutions += 1

                break
            
