import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pandas as pd

plotting = False
paused = False

columns = ["Waktu", "Arus (mA)", "Tegangan (V)", "Resistansi (Ohm)"]
df = pd.DataFrame(columns=columns)

# ---- Memulai setting port serial ---
import serial
from serial.tools import list_ports
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


def toggle_start_stop():
    global plotting, df, paused
    plotting = not plotting
    if plotting:
        paused = False
        start_stop_button.configure(text="Stop", fg_color="red")
        info_label.configure(text="Start Plotting")
        df = pd.DataFrame(columns=columns)
        reset_plot()
    else:
        start_stop_button.configure(text="Start", fg_color="#1F6AA5")
        info_label.configure(text="Stop Plotting")

def toggle_pause_resume():
    global paused
    paused = not paused
    if paused:
        pause_resume_button.configure(text="Resume")
        info_label.configure(text="Plotting Paused")
    else:
        pause_resume_button.configure(text="Pause")
        info_label.configure(text="Plotting")

def set_plot_format(ax, title, ylabel):
    ax.set_xlabel("Waktu")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc='upper left')#, bbox_to_anchor=(1, 1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.tick_params(axis='x', rotation=30)

def plot_multimeter():
    global columns, df, plotting, serial_port, paused
    if plotting and not paused:
        info_label.configure(text="Plotting")
        try:
            value_sensor = serial_port.readline().decode().rstrip().split('\t')
            if value_sensor != '':
                value_sensor = list(map(float, value_sensor))
                value_sensor = value_sensor[:len(columns)-1]        # Untuk Tes

            while len(value_sensor) < len(columns) - 1:
                value_sensor.append(0)  # Tambahkan nilai NaN jika kurang

            value_label.configure(text=value_sensor, font=ctk.CTkFont('calibri', 16))

            waktu_sekarang = pd.Timestamp.now()
            data = [waktu_sekarang] + value_sensor

            if len(df) == 0:
                df = pd.DataFrame([data], columns=columns)
            else:
                new_row = pd.DataFrame([data], columns=columns)
                df = pd.concat([df, new_row], ignore_index=True)

            # ================== Amperemeter ========================
            value_ampere.configure(text=str(df["Arus (mA)"].iloc[-1]) + " mA")
            ax_ampere.clear()
            ax_ampere.plot(df['Waktu'], df["Arus (mA)"], label="Arus (mA)")
            set_plot_format(ax_ampere, "Grafik I - t", "Arus (mA)")
            canvas_ampere.draw_idle()

            # ================== Voltmeter ========================
            value_volt.configure(text=str(df["Tegangan (V)"].iloc[-1]) +" V")
            ax_volt.clear()
            ax_volt.plot(df['Waktu'], df["Tegangan (V)"], label="Tegangan (V)")
            set_plot_format(ax_volt, "Grafik V - t", "Tegangan (V)")
            canvas_volt.draw_idle()

            # ================== Ohmmeter ========================
            value_resistance.configure(text=str(df["Resistansi (Ohm)"].iloc[-1])+ " Ohm")
            ax_resistance.clear()
            ax_resistance.plot(df['Waktu'], df["Resistansi (Ohm)"], label="Resistansi (Ohm)")
            set_plot_format(ax_resistance, "Grafik R - t", "Resistansi (Ohm)")
            canvas_resistance.draw_idle()
        except:
            pass

    root.update()
    root.after(100, plot_multimeter)

def reset_plot():
    # ================== Amperemeter ========================
    ax_ampere.clear()
    ax_ampere.plot([], [], label="Arus (mA)")
    set_plot_format(ax_ampere, "Grafik I - t", "Arus (mA)")
    canvas_ampere.draw()

    # ================== Voltmeter ========================
    ax_volt.clear()
    ax_volt.plot([], [], label="Tegangan (V)")
    set_plot_format(ax_volt, "Grafik V - t", "Tegangan (V)")
    canvas_volt.draw()

    # ================== Ohmmeter ========================
    ax_resistance.clear()
    ax_resistance.plot([], [], label="Resistansi (Ohm)")
    set_plot_format(ax_resistance, "Grafik R - t", "Resistansi (Ohm)")
    canvas_resistance.draw()

# ======================= GUI =======================
root = ctk.CTk()
root.title('Multimeter Digital GUI')
root.geometry("550x700")  # Setting ukuran tampilan

frame_root = ctk.CTkFrame(root)
frame_root.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
#frame_root.rowconfigure([0, 1, 2, 3], weight=1)

title_frame = ctk.CTkFrame(frame_root)
title_frame.grid(column=0, row=0, sticky="nsew")
title_label = ctk.CTkLabel(master=title_frame, text="Multimeter Digital Arduino", justify="center", font=ctk.CTkFont('calibri', 32))
title_label.pack(expand=True, fill=tk.X)

plot_frame = ctk.CTkFrame(frame_root)
plot_frame.grid(column=0, row=1, sticky="nsew")

tabview = ctk.CTkTabview(master=plot_frame)
tabview.grid(column=0, row=0, sticky="nsew")
f1 = tabview.add('Amperemeter')
f2 = tabview.add('Voltmeter')
f3 = tabview.add('Ohmmeter')

# ================== Amperemeter ========================
frame_ampere = ctk.CTkFrame(f1)
frame_ampere.grid(column=0, row=0, sticky="nsew")
fig_ampere, ax_ampere = plt.subplots(constrained_layout=True)
canvas_ampere = FigureCanvasTkAgg(fig_ampere, master=frame_ampere)
canvas_widget_ampere = canvas_ampere.get_tk_widget()
canvas_widget_ampere.grid(row=0, column=0, sticky="nsew")
value_ampere = ctk.CTkLabel(frame_ampere, text="Sensor Value", font=ctk.CTkFont('calibri', 16))
value_ampere.grid(row=1, column=0, sticky="ns", pady=5)

# ================== Voltmeter ========================
frame_volt = ctk.CTkFrame(f2)
frame_volt.grid(column=1, row=0, sticky="nsew")
fig_volt, ax_volt = plt.subplots(constrained_layout=True)
canvas_volt = FigureCanvasTkAgg(fig_volt, master=frame_volt)
canvas_widget_volt = canvas_volt.get_tk_widget()
canvas_widget_volt.grid(row=0, column=0, sticky="nsew")
value_volt = ctk.CTkLabel(frame_volt, text="Sensor Value", font=ctk.CTkFont('calibri', 16))
value_volt.grid(row=1, column=0, sticky="ns", pady=5)

# ================== Ohmmeter ========================
frame_resistance = ctk.CTkFrame(f3)
frame_resistance.grid(column=2, row=0, sticky="nsew")
fig_resistance, ax_resistance = plt.subplots(constrained_layout=True)
canvas_resistance = FigureCanvasTkAgg(fig_resistance, master=frame_resistance)
canvas_widget_resistance = canvas_resistance.get_tk_widget()
canvas_widget_resistance.grid(row=0, column=0, sticky="nsew")
value_resistance = ctk.CTkLabel(frame_resistance, text="Sensor Value", font=ctk.CTkFont('calibri', 16))
value_resistance.grid(row=1, column=0, sticky="ns", pady=5)

reset_plot()

button_frame = ctk.CTkFrame(frame_root, width=600)
button_frame.grid(column=0, row=2, sticky="nsew", padx=10, pady=10)
button_frame.rowconfigure(0, weight=1)
button_frame.columnconfigure([0, 1, 2, 3], weight=1)

start_stop_button = ctk.CTkButton(button_frame, text="Start", command=toggle_start_stop)
start_stop_button.grid(row=0, column=0,sticky="nsew", padx=10)
pause_resume_button = ctk.CTkButton(button_frame, text="Pause", command=toggle_pause_resume)
pause_resume_button.grid(row=0, column=1, sticky="nsew", padx=10)
reset_button = ctk.CTkButton(button_frame, text="Reset", command=reset_plot)
reset_button.grid(row=0, column=2, sticky="nsew", padx=10)

data_frame = ctk.CTkFrame(frame_root)
data_frame.grid(column=0, row=4, sticky="nsew", padx=10, pady=10)
data_frame.grid_rowconfigure([0, 1], weight=1)
data_frame.grid_columnconfigure(0, weight=1)

value_label = ctk.CTkLabel(data_frame, text="Sensor Value", font=ctk.CTkFont('calibri', 16))
value_label.grid(row=0, column=0, sticky="ns")

info_frame = ctk.CTkFrame(frame_root)
info_frame.grid(column=0, row=4, sticky="nsew", padx=10, pady=10)
info_frame.grid_rowconfigure([0, 1], weight=1)
info_frame.grid_columnconfigure(0, weight=1)
info_label = ctk.CTkLabel(info_frame, text="Port", font=ctk.CTkFont('calibri', 16))
info_label.grid(row=1, column=0, sticky="ns")

root.after(100, plot_multimeter)
root.mainloop()
