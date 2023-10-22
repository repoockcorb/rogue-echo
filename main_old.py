import sys
import random
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QStatusBar, QTabWidget
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QPixmap

class MovingGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rogue Air Braked Power Monitor")
        self.setGeometry(100, 100, 1000, 600)  # Increase the window width to accommodate the image

        self.max_time_window = 5  # Maximum time window to display in seconds

        self.elapsed_time = 0  # Initialize the elapsed time to 0

        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        # Create the first tab
        self.tab1 = QWidget()
        self.central_widget.addTab(self.tab1, "Graph")

        self.main_layout = QHBoxLayout(self.tab1)

        # Create the left layout for the graph and other items
        self.graph_layout = QVBoxLayout()
        self.main_layout.addLayout(self.graph_layout)

        self.weight_label = QLabel("Enter weight (kg):")
        self.weight_input = QLineEdit()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.clear_button = QPushButton("Clear")
        self.export_button = QPushButton("Export Data")

        self.graph_layout.addWidget(self.weight_label)
        self.graph_layout.addWidget(self.weight_input)
        self.graph_layout.addWidget(self.start_button)
        self.graph_layout.addWidget(self.stop_button)
        self.graph_layout.addWidget(self.clear_button)
        self.graph_layout.addWidget(self.export_button)

        # Additional input fields for the two lines
        self.line1_label = QLabel("Enter line 1 (W/kg):")
        self.line1_input = QLineEdit()
        self.graph_layout.addWidget(self.line1_label)
        self.graph_layout.addWidget(self.line1_input)

        self.line2_label = QLabel("Enter line 2 (W/kg):")
        self.line2_input = QLineEdit()
        self.graph_layout.addWidget(self.line2_label)
        self.graph_layout.addWidget(self.line2_input)

        self.plot_widget = pg.PlotWidget(background='w')
        self.graph_layout.addWidget(self.plot_widget)

        self.start_button.clicked.connect(self.start_plotting)
        self.stop_button.clicked.connect(self.stop_plotting)
        self.clear_button.clicked.connect(self.clear_plot)
        self.export_button.clicked.connect(self.export_data)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)

        self.data_x = []
        self.data_y = []
        self.start_time = QDateTime.currentDateTime()  # Variable to store the start time of the plot
        self.time_interval = 10  # Default time interval (in seconds)

        self.line1_watts_per_kg = 0
        self.line2_watts_per_kg = 0

        self.line1 = pg.InfiniteLine(pos=0, angle=0, movable=False, pen=pg.mkPen('r', width=2))
        self.line2 = pg.InfiniteLine(pos=0, angle=0, movable=False, pen=pg.mkPen('g', width=2))
        self.plot_widget.addItem(self.line1)
        self.plot_widget.addItem(self.line2)

        self.plot_widget.setLabel("left", "Watts/Kilogram")
        self.plot_widget.setLabel("bottom", "Time (s)")
        self.plot_widget.setTitle("Watts per Kilogram Vs. Time")

        self.plot_widget.showGrid(x=True, y=True)

        # Plot initial data points (optional)
        self.plot_widget.plot(self.data_x, self.data_y, pen=None, symbol='o', symbolPen='r', symbolBrush='r')

        self.is_plotting = False

        # Create the status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Create version and "Developed by" labels for the status bar
        self.version_label = QLabel("Version 1.0")  # Replace "1.0" with the actual version number
        self.developed_by_label = QLabel("Developed by Brock Cooper")  # Replace "Your Name" with the developer's name

        # Add the version label to the left side of the status bar
        self.statusBar.addWidget(self.version_label, 1)

        # Add the "Developed by" label to the bottom right corner of the status bar
        self.statusBar.addPermanentWidget(self.developed_by_label)

        # Create the layout for the image at the bottom-right corner
        self.image_layout = QVBoxLayout()
        self.main_layout.addLayout(self.image_layout)

        # Create a QLabel widget to display the image
        self.image_label = QLabel()
        image_path = "rogue-echo-air-bike.jpg"
        image_pixmap = QPixmap(image_path)
        self.image_label.setPixmap(image_pixmap)
        self.image_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)  # Align the image to the bottom-right corner

        # Add the image to the right-hand side layout
        self.image_layout.addWidget(self.image_label)

        

    def start_plotting(self):
        if not self.is_plotting:
            weight_str = self.weight_input.text()
            try:
                weight_kg = float(weight_str)
            except ValueError:
                self.show_error_message("Invalid input", "Please enter a valid weight in kilograms.")
                return

            line1_str = self.line1_input.text()
            try:
                self.line1_watts_per_kg = float(line1_str)
            except ValueError:
                self.show_error_message("Invalid input", "Please enter a valid value for Line 1 (W/kg).")
                return

            line2_str = self.line2_input.text()
            try:
                self.line2_watts_per_kg = float(line2_str)
            except ValueError:
                self.show_error_message("Invalid input", "Please enter a valid value for Line 2 (W/kg).")
                return

            self.weight_kg = weight_kg
            self.start_time = QDateTime.currentDateTime()  # Record the start time

            # Set the positions and orientations of the two lines based on user input
            self.line1.setPos(self.line1_watts_per_kg)
            self.line1.setAngle(0)  # Horizontal line
            self.line2.setPos(self.line2_watts_per_kg)
            self.line2.setAngle(0)  # Horizontal line

            # Set the view range of the plot to make sure the lines are visible
            min_watts_per_kg = min(self.line1_watts_per_kg, self.line2_watts_per_kg) - 1
            max_watts_per_kg = max(self.line1_watts_per_kg, self.line2_watts_per_kg) + 1
            self.plot_widget.setYRange(min_watts_per_kg, max_watts_per_kg)

            # Clear data points
            self.data_x.clear()
            self.data_y.clear()

            self.timer.start(10)  # Update the plot every 10 milliseconds (0.1 seconds)
            self.is_plotting = True

    def stop_plotting(self):
        if self.is_plotting:
            self.timer.stop()
            self.is_plotting = False



    def update_plot(self):
        if self.is_plotting:
            # Increment the elapsed time by the time interval for each new data point
            elapsed_time = self.elapsed_time + self.time_interval

            # Simulate getting a new data point
            watts = random.uniform(50, 400)  # Random value between 50 to 400 watts

            # Calculate watts per kilogram
            watts_per_kg = watts / self.weight_kg

            # Append data points to the lists
            self.data_x.append(elapsed_time)
            self.data_y.append(watts_per_kg)

            # Smooth the data using a moving average with a window of size 5
            if len(self.data_y) >= 5:
                smoothed_data = np.convolve(self.data_y[-5:], np.ones(5) / 5, mode='valid')
                self.data_y[-1] = smoothed_data[-1]

            # Calculate the start time for the visible range based on the max_time_window
            start_time_visible = max(0, elapsed_time - self.max_time_window)

            # Clear the plot widget and add the lines
            self.plot_widget.clear()
            self.plot_widget.addItem(self.line1)
            self.plot_widget.addItem(self.line2)

            # Plot the blue line (calculated data) without clearing the previous plot
            self.plot_widget.plot(self.data_x, self.data_y, pen=pg.mkPen('b', width=2))

            # Set the visible range for the x-axis to show the last self.max_time_window seconds of data
            self.plot_widget.setXRange(start_time_visible, elapsed_time)

            # Limit the number of data points shown on the plot
            max_data_points = 1000
            if len(self.data_x) > max_data_points:
                self.data_x = self.data_x[-max_data_points:]
                self.data_y = self.data_y[-max_data_points:]

            # Update the elapsed time
            self.elapsed_time = elapsed_time




    def clear_plot(self):
        self.stop_plotting()  # Stop updating the plot
        self.data_x.clear()
        self.data_y.clear()
        self.plot_widget.clear()
        self.plot_widget.addItem(self.line1)
        self.plot_widget.addItem(self.line2)
        self.is_plotting = False

        # # Reset the start_time to the current time
        # self.start_time = QDateTime.currentDateTime()

    def export_data(self):
        if not self.data_x:
            self.show_error_message("No Data", "There is no data to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            data = np.column_stack((self.data_x, self.data_y))
            header = 'Time (s), Watts per Kilogram'
            fmt = '%.2f'  # Format the time values with 2 decimal places
            np.savetxt(file_path, data, delimiter=',', header=header, fmt=fmt)

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovingGraphApp()
    window.show()
    sys.exit(app.exec_())

