import sys
import random
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QStatusBar, QTabWidget, QComboBox
from PyQt5.QtCore import QTimer, QDateTime, Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QPixmap
import serial
from serial.tools import list_ports
import os
import time

# Plotting Variables:
resolution = 0.1  # plot every 0.1 seconds

# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")

#     return os.path.join(base_path, relative_path)

# Logo = resource_path("rogue-echo-air-bike.jpg")


# def get_path(filename):
#     if hasattr(sys, "_MEIPASS"):
#         return os.path.join(sys._MEIPASS, filename)
#     else:
#         return filename

class RPMWorker(QObject):
    update_rpm_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial_connection = None
        self.stop_rpm_flag = False

    def connect_serial(self, com_port):
        try:
            self.serial_connection = serial.Serial(com_port, 9600, timeout=1)
            self.update_rpm_signal.emit("Connected to Rogue Echo Bike")
        except Exception as e:
            self.update_rpm_signal.emit(str(e))

    def read_rpm(self):
        while not self.stop_rpm_flag:
            try:
                rpm = self.serial_connection.readline().decode().strip()
                if rpm:
                    self.update_rpm_signal.emit(rpm)
            except Exception as e:
                self.update_rpm_signal.emit(str(e))
        # Close the serial connection when stopping
        if self.serial_connection:
            self.serial_connection.close()

    def stop_rpm(self):
        self.stop_rpm_flag = True


class MovingGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rogue Air Braked Power Monitor")
        self.setGeometry(100, 100, 1000, 600)

        self.max_time_window = 15
        self.elapsed_time = 0

        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        self.tab1 = QWidget()
        self.central_widget.addTab(self.tab1, "Graph")

        self.main_layout = QHBoxLayout(self.tab1)

        self.graph_layout = QVBoxLayout()
        self.main_layout.addLayout(self.graph_layout)

        self.com_port_label = QLabel("Select COM Port:")
        self.com_port_combo = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.populate_com_ports)

        self.weight_label = QLabel("Enter weight (kg):")
        self.weight_input = QLineEdit()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.clear_button = QPushButton("Clear")
        self.export_button = QPushButton("Export Data")

        com_port_layout = QHBoxLayout()
        com_port_layout.addWidget(self.com_port_label)
        com_port_layout.addWidget(self.com_port_combo)
        com_port_layout.addWidget(self.refresh_button)

        self.graph_layout.addLayout(com_port_layout)

        self.graph_layout.addWidget(self.weight_label)
        self.graph_layout.addWidget(self.weight_input)
        self.graph_layout.addWidget(self.start_button)
        self.graph_layout.addWidget(self.stop_button)
        self.graph_layout.addWidget(self.clear_button)
        self.graph_layout.addWidget(self.export_button)

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
        self.start_time = QDateTime.currentDateTime()

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

        self.is_plotting = False

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.version_label = QLabel("Version 1.0")
        self.developed_by_label = QLabel("Developed by Brock Cooper")

        self.statusBar.addWidget(self.version_label, 1)
        self.statusBar.addPermanentWidget(self.developed_by_label)

        self.image_layout = QVBoxLayout()
        self.main_layout.addLayout(self.image_layout)

        self.image_label = QLabel()
        image_path = "rogue-echo-air-bike.jpg"
        image_pixmap = QPixmap(image_path)
        self.image_label.setPixmap(image_pixmap)
        self.image_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        self.image_layout.addWidget(self.image_label)

        self.rpm_label = QLabel("RPM: 0")
        self.graph_layout.addWidget(self.rpm_label)

        # Create the RPM worker and connect its signal to the update_rpm_display method
        self.rpm_worker = RPMWorker()
        self.rpm_worker.update_rpm_signal.connect(self.update_rpm_display)

    def populate_com_ports(self):
        com_ports = list(set([port.device for port in list_ports.comports()]))
        self.com_port_combo.clear()
        self.com_port_combo.addItems(com_ports)

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
            self.start_time = QDateTime.currentDateTime()

            self.line1.setPos(self.line1_watts_per_kg)
            self.line1.setAngle(0)
            self.line2.setPos(self.line2_watts_per_kg)
            self.line2.setAngle(0)

            min_watts_per_kg = min(self.line1_watts_per_kg, self.line2_watts_per_kg) - 1
            max_watts_per_kg = max(self.line1_watts_per_kg, self.line2_watts_per_kg) + 1
            self.plot_widget.setYRange(min_watts_per_kg, max_watts_per_kg)

            self.data_x.clear()
            self.data_y.clear()

            self.timer.start(int(resolution * 1000))
            self.is_plotting = True

            # Connect to the selected COM port
            com_port = self.com_port_combo.currentText()
            self.rpm_worker.connect_serial(com_port)

            # If there is a previous RPM thread running, stop it and wait for it to finish
            if hasattr(self, 'rpm_thread') and self.rpm_thread.isRunning():
                self.rpm_worker.stop_rpm()
                self.rpm_thread.quit()
                self.rpm_thread.wait()

            
            # Start a new RPM thread
            self.rpm_thread = QThread()
            self.rpm_worker.moveToThread(self.rpm_thread)
            self.rpm_thread.started.connect(self.rpm_worker.read_rpm)
            self.rpm_thread.start()

            # self.rpm_thread = QThread()
            # self.rpm_worker = RPMWorker()  # Create a new RPMWorker instance
            # self.rpm_worker.update_rpm_signal.connect(self.update_rpm_display)
            # self.rpm_worker.moveToThread(self.rpm_thread)
            # self.rpm_thread.started.connect(self.rpm_worker.read_rpm)
            # self.rpm_thread.start()

    def stop_plotting(self):
        if self.is_plotting:
            self.timer.stop()
            self.is_plotting = False

            # Stop the RPM thread and close the serial connection
            self.rpm_worker.stop_rpm()
            self.rpm_thread.quit()
            self.rpm_thread.wait()


    def update_plot(self):
        if self.is_plotting:
            elapsed_time = self.elapsed_time + resolution

            # Simulate getting a new data point
            watts = random.uniform(50, 400)  # Replace this with actual data from your device

            watts_per_kg = watts / self.weight_kg

            self.data_x.append(elapsed_time)
            self.data_y.append(watts_per_kg)

            if len(self.data_y) >= 5:
                smoothed_data = np.convolve(self.data_y[-5:], np.ones(5) / 5, mode='valid')
                self.data_y[-1] = smoothed_data[-1]

            start_time_visible = max(0, elapsed_time - self.max_time_window)

            self.plot_widget.clear()
            self.plot_widget.addItem(self.line1)
            self.plot_widget.addItem(self.line2)

            self.plot_widget.plot(self.data_x, self.data_y, pen=pg.mkPen('b', width=2))

            self.plot_widget.setXRange(start_time_visible, elapsed_time)

            max_data_points = 1000
            if len(self.data_x) > max_data_points:
                self.data_x = self.data_x[-max_data_points:]
                self.data_y = self.data_y[-max_data_points:]

            self.elapsed_time = elapsed_time

    def clear_plot(self):
        self.stop_plotting()
        self.data_x.clear()
        self.data_y.clear()
        self.elapsed_time = 0
        self.plot_widget.clear()
        self.plot_widget.addItem(self.line1)
        self.plot_widget.addItem(self.line2)
        self.is_plotting = False

    def export_data(self):
        if not self.data_x:
            self.show_error_message("No Data", "There is no data to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            start_time = self.elapsed_time - len(self.data_x) * resolution
            time_values = np.arange(start_time, self.elapsed_time, resolution)
            export_data = np.column_stack((time_values, self.data_y))
            header = 'Time (s), Watts per Kilogram'
            fmt = '%.2f'
            np.savetxt(file_path, export_data, delimiter=',', header=header, fmt=fmt)

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def update_rpm_display(self, rpm):
        self.rpm_label.setText(f"RPM: {rpm}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovingGraphApp()
    window.show()
    sys.exit(app.exec_())
