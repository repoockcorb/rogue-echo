import subprocess

pyinstaller_command = [
    "pyinstaller",
    "main.py",
    "--name", "Rogue-Echo-Bike",
    "--onefile",
    "--windowed",
    "--icon=rogue_echo.ico",
    "--add-data", "rogue-echo-air-bike.jpg;."
    # "--icon=C:\\Users\\bcoo6642\\OneDrive - The University of Sydney (Staff)\\Desktop\\Air Braked Bike\\rogue_echo.ico",
    # "--add-data", "C:\\Users\\bcoo6642\\OneDrive - The University of Sydney (Staff)\\Desktop\\Air Braked Bike\\rogue-echo-air-bike.jpg;."
]

subprocess.call(pyinstaller_command)
