import customtkinter as ctk
from CTkTable import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import time
import serial
from serial.tools import list_ports
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Global variables
columns = ["Waktu (t)", "Arus (mA)", "Tegangan (V)", "Resistansi (Ohm)"]
df = pd.DataFrame(columns=columns)
df_data = pd.DataFrame(columns=columns)
plotting = False
paused = False
serial_port = None

# --- Serial port functions ---
def get_ports():
    ports = list_ports.comports()
    for port in ports:
        if '/dev/tty' in port.device or port.device.startswith('COM'):
            return port.device
    return None

def connect_to_arduino():
    global serial_port, port
    try:
        port = get_ports()
        if port:
            serial_port = serial.Serial(port, 9600)
            serial_port.reset_input_buffer()
            return True
    except PermissionError as e:
        if e.errno == 13:  # Access is denied error
            logging.error(f"Permission Error: {e}")
            Arduino_label.configure(text="Akses Ditolak, coba lagi atau periksa perangkat.")
        serial_port = None
        return False
    except serial.SerialException as e:
        logging.error(f"Serial Error: {e}")
        Arduino_label.configure(text="Kesalahan Serial, coba lagi atau periksa perangkat.")
        serial_port = None
        return False
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        Arduino_label.configure(text="Kesalahan Tak Terduga, coba lagi.")
        serial_port = None
        return False

def update_arduino_state():
    if serial_port and serial_port.is_open:
        Arduino_label.configure(text=f"Arduino Terhubung Pada {port}")
    else:
        Arduino_label.configure(text="Arduino Terputus. Mencoba menghubungkan kembali...")
        if not connect_to_arduino():
            logging.info("Gagal menghubungkan kembali. Memeriksa kembali dalam 5 detik.")
            root.after(5000, update_arduino_state)

# --- Plotting functions ---
def set_plot_format(ax, title, xlabel, ylabel, label, reset=False):
    global df_data
    ax.clear()
    ax.plot([], [], label=label) if reset else ax.plot(df_data[xlabel], df_data[ylabel], label=label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc='upper left')

    if xlabel == columns[0]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.tick_params(axis='x', rotation=30)

def add_data():
    global df_data, df
    if df_data.empty:
        df_data = df.copy()
    else:
        df_data = pd.concat([df_data, df], ignore_index=True)

    update_plots()
    data_percobaan = df_data.values.tolist()
    data_percobaan.insert(0, columns)
    table.update_values(data_percobaan)

def update_plots():
    set_plot_format(ax_ampere, "Grafik V-R", columns[2], columns[3], columns[1])
    set_plot_format(ax_volt, "Grafik I-R", columns[1], columns[3], columns[2])
    set_plot_format(ax_resistance, "Grafik V-I", columns[2], columns[1], columns[3])
    canvas_ampere.draw_idle()
    canvas_volt.draw_idle()
    canvas_resistance.draw_idle()

def plot_multimeter():
    global df, df_data, serial_port
    if plotting and not paused and serial_port is not None:
        try:
            value_sensor = serial_port.readline().decode().rstrip().split('\t')
            if value_sensor:
                value_sensor = list(map(float, value_sensor[:len(columns)-1]))
                value_sensor.extend([0] * (len(columns) - 1 - len(value_sensor)))

                waktu_sekarang = pd.Timestamp.now()
                data = [waktu_sekarang] + value_sensor

                df = pd.DataFrame([data], columns=columns)
                df[columns[0]] = df[columns[0]].dt.strftime('%H:%M:%S')
                values = df.values.tolist()
                values.insert(0, columns)
                table_now.update_values(values)

        except Exception as e:
            logging.error(f"Error in plot_multimeter: {e}")
            Arduino_label.configure(text=f"{e}")
            serial_port = None

    root.after(100, plot_multimeter)

def reset_plot():
    update_plots()
    canvas_ampere.draw()
    canvas_volt.draw()
    canvas_resistance.draw()

def export_data():
    global df
    df.to_excel("Data_Percobaan.xlsx", index=False)

# --- GUI Initialization ---
def initialize_gui_elements():
    initialize_title_frame()
    initialize_arduino_frame()
    initialize_button_frame()
    initialize_plot_frame()
    initialize_data_frame()
    connect_to_arduino()
    update_arduino_state()
    root.after(100, plot_multimeter)

def initialize_title_frame():
    title_frame = ctk.CTkFrame(frame_root)
    title_frame.grid(column=0, row=0, sticky="nsew")
    title_label = ctk.CTkLabel(master=title_frame, text="Multimeter Digital Arduino", justify="center",
                            font=ctk.CTkFont('calibri', 32))
    title_label.pack(expand=True, fill=ctk.X)

def initialize_arduino_frame():
    Arduino_frame = ctk.CTkFrame(frame_root)
    Arduino_frame.grid(column=0, row=1, sticky="nsew", padx=10, pady=10)
    Arduino_frame.grid_rowconfigure([0, 1], weight=1)
    Arduino_frame.grid_columnconfigure(0, weight=1)
    global Arduino_label
    Arduino_label = ctk.CTkLabel(Arduino_frame, text="Port", font=ctk.CTkFont('calibri', 16))
    Arduino_label.grid(row=1, column=0, sticky="ns")

def initialize_button_frame():
    button_frame = ctk.CTkFrame(frame_root, width=600)
    button_frame.grid(column=0, row=2, sticky="nsew", padx=10, pady=10)
    button_frame.rowconfigure(0, weight=1)
    button_frame.columnconfigure([0, 1, 2, 3], weight=1)
    global start_stop_button, pause_resume_button, reset_button
    start_stop_button = ctk.CTkButton(button_frame, text="Start", command=toggle_start_stop)
    start_stop_button.grid(row=0, column=0, sticky="nsew", padx=10)
    pause_resume_button = ctk.CTkButton(button_frame, text="Pause", command=toggle_pause_resume)
    pause_resume_button.grid(row=0, column=1, sticky="nsew", padx=10)
    reset_button = ctk.CTkButton(button_frame, text="Reset", command=reset_plot)
    reset_button.grid(row=0, column=2, sticky="nsew", padx=10)

def initialize_plot_frame():
    plot_frame = ctk.CTkFrame(frame_root)
    plot_frame.grid(column=0, row=3, sticky="nsew")
    tabview = ctk.CTkTabview(master=plot_frame, height=440)
    tabview.grid(column=0, row=0, sticky="nsew")
    f1 = tabview.add("Grafik V-R")
    f2 = tabview.add("Grafik I-R")
    f3 = tabview.add("Grafik V-I")
    f4 = tabview.add("Data Percobaan")

    global fig_ampere, ax_ampere, canvas_ampere, fig_volt, ax_volt, canvas_volt
    global fig_resistance, ax_resistance, canvas_resistance

    fig_ampere, ax_ampere, canvas_ampere = create_plot_frame(f1)
    fig_volt, ax_volt, canvas_volt = create_plot_frame(f2)
    fig_resistance, ax_resistance, canvas_resistance = create_plot_frame(f3)
    
    reset_plot()
    frame_table = ctk.CTkFrame(f4)
    frame_table.grid(column=0, row=0, sticky="nsew")
    global table
    table = CTkTable(master=frame_table,values=[columns],header_color="dark blue",width=128,padx=0,row=10)
    table.grid(column=0, row=0, sticky="nsew")

    export_button = ctk.CTkButton(frame_table, text="Ekspor Data", command=export_data)
    export_button.grid(column=0, row=1, sticky="nsew", padx=10, pady=10)


def create_plot_frame(tab_name):
    frame = ctk.CTkFrame(tab_name)
    frame.grid(column=0, row=0, sticky="nsew")
    fig, ax = plt.subplots(constrained_layout=True)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    return fig, ax, canvas

def initialize_data_frame():
    data_frame = ctk.CTkFrame(frame_root)
    data_frame.grid(column=0, row=4, sticky="nsew", padx=10, pady=10)
    global table_now
    table_now = CTkTable(master=data_frame, values=[columns], header_color="dark blue", width=128, padx=0, row=2)
    table_now.grid(column=0, row=0, sticky="nsew")
    add_button = ctk.CTkButton(data_frame, text="Tambah Data", command=add_data)
    add_button.grid(column=0, row=1, sticky="nsew", padx=10, pady=10)

def toggle_start_stop():
    global plotting
    plotting = not plotting
    start_stop_button.configure(text="Stop" if plotting else "Start")
    if plotting:
        pause_resume_button.configure(state="normal")
    else:
        pause_resume_button.configure(text="Pause", state="disabled")

def toggle_pause_resume():
    global paused
    paused = not paused
    pause_resume_button.configure(text="Resume" if paused else "Pause")

# --- Main Program ---
root = ctk.CTk()
frame_root = ctk.CTkFrame(root)
frame_root.grid(row=0, column=0, sticky="nsew")
root.geometry("540x700")
initialize_gui_elements()
root.mainloop()
