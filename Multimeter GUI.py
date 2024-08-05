import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np
import pandas as pd

columns = ["Time", "Arus (mA)", "Tegangan (V)", "Resistansi (Ohm)"]
df = pd.DataFrame(columns=columns)

# ---- Memulai setting port serial ---
from serial.tools import list_ports
import serial

def get_ports():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if '/dev/tty' in port.device or port.device.startswith('COM'):
            # Memeriksa jika port berada di /dev/tty atau dimulai dengan COM di Windows
            print(f"Detected port: {port.device}, Description: {port.description}")
            return port.device
    return None

serial_port = serial.Serial(get_ports(), 9600)
serial_port.reset_input_buffer()

# ======================= GUI =======================
root = tk.Tk()
root.title('Astaghfirullah GPP.kok')
root.geometry("500x700")  # Setting ukuran tampilan

frame_root = ttk.Frame(root)
frame_root.pack()
