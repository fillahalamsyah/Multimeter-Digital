import customtkinter as ctk
from CTkTable import CTkTable
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import serial
from serial.tools import list_ports

# Global variables
columns = ["Waktu (t)", "Arus (A)", "Tegangan (V)", "Resistansi (Ohm)"]
df = pd.DataFrame(columns=columns) # Dataframe untuk menyimpan data saat ini
df_all = pd.DataFrame(columns=columns) # Dataframe untuk menyimpan semua data percobaan
df_data = pd.DataFrame(columns=columns) # Dataframe untuk menyimpan data percobaan saat ini
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
    except (PermissionError, serial.SerialException, Exception) as e:
        serial_port = None
        Arduino_label.configure(text=f"Kesalahan: {e}")
        return False

def update_arduino_state():
    if serial_port and serial_port.is_open:
        Arduino_label.configure(text=f"Arduino Terhubung Pada {port}")
    else:
        Arduino_label.configure(text="Arduino Terputus. Mencoba menghubungkan kembali...")
        if not connect_to_arduino():
            root.after(5000, update_arduino_state)

# --- Plotting functions ---
def set_plot_format(ax, title, xlabel, ylabel, label, reset=False):
    global df_data, df, df_all

    ax.clear()

    if title == "Grafik (V,I,R)-t":
        # Plot grafik V-I-R dengan sumbu x waktu (t) dan sumbu y V, I, R
        ax.plot([[],[],[]], [[],[],[]]) if reset else ax.plot(df_all[xlabel],df_all.iloc[:, 1:], label=df_all.columns[1:])
    else:
        ax.plot([], [], label=label) if reset else ax.plot(df_data[xlabel], df_data[ylabel], label=label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if not reset:
        ax.legend(loc='upper left')

    if xlabel == columns[0]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.tick_params(axis='x', rotation=30)

def add_data():
    global df_data, df
    df_data = pd.concat([df_data, df], ignore_index=True) if not df_data.empty else df.copy()
    update_plots()
    data_percobaan = df_data.values.tolist()
    data_percobaan.insert(0, columns)
    table.update_values(data_percobaan)

def update_plots():
    # set_plot_format(ax_all, "Grafik (V,I,R)-t", columns[0], columns[1], columns[2])
    # canvas_all.draw_idle()

    #set_plot_format(ax_all, "Grafik (V,I,R)-t", columns[0], "Nilai", columns[1:])
    set_plot_format(ax_ampere, "Grafik V-R", columns[2], columns[3], columns[1])
    set_plot_format(ax_volt, "Grafik I-R", columns[1], columns[3], columns[2])
    set_plot_format(ax_resistance, "Grafik V-I", columns[2], columns[1], columns[3])
    
    canvas_ampere.draw_idle()
    canvas_volt.draw_idle()
    canvas_resistance.draw_idle()

def plot_multimeter():
    global df, df_data, df_all, serial_port
    if plotting and not paused and serial_port is not None:
        try:
            value_sensor = serial_port.readline().decode().rstrip().split('\t')
            if value_sensor:
                value_sensor = list(map(float, value_sensor[:len(columns)-1]))
                value_sensor.extend([0] * (len(columns) - 1 - len(value_sensor)))

                waktu_sekarang = pd.Timestamp.now()
                data = [waktu_sekarang] + value_sensor

                df = pd.DataFrame([data], columns=columns)
                df[columns[0]] = df[columns[0]]
                
                df_all = pd.concat([df_all, df], ignore_index=True) if not df_all.empty else df.copy()
                
                set_plot_format(ax_all, "Grafik (V,I,R)-t", columns[0], "Nilai", columns[1:])
                canvas_all.draw_idle()
                
                values = df.values.tolist()
                values.insert(0, columns)
                table_now.update_values(values)

        except Exception as e:
            Arduino_label.configure(text=f"{e}")
            serial_port = None

    root.after(500, plot_multimeter)

def reset_plot():
    global df_all, df_data
    set_plot_format(ax_all, "Grafik (V,I,R)-t", columns[0], "Nilai", columns[1:], reset=True)
    set_plot_format(ax_ampere, "Grafik V-R", columns[2], columns[3], columns[1], reset=True)
    set_plot_format(ax_volt, "Grafik I-R", columns[1], columns[3], columns[2], reset=True)
    set_plot_format(ax_resistance, "Grafik V-I", columns[2], columns[1], columns[3], reset=True)
    
    #update_plots()
    canvas_all.draw()
    canvas_ampere.draw()
    canvas_volt.draw()
    canvas_resistance.draw()

def export_data():
    global df_all, df_data
    import openpyxl
    with pd.ExcelWriter("Data_Multimeter.xlsx", engine='openpyxl') as writer:
        df_data.to_excel(writer, sheet_name="Data_Percobaan_Saat_Ini", index=False)
        df_all.to_excel(writer, sheet_name="Data_Keseluruhan", index=False)
        Arduino_label.configure(text="Data berhasil diekspor ke Data_Multimeter.xlsx")
# --- GUI Initialization ---
def initialize_gui():
    title_label = ctk.CTkLabel(frame_root, text="Multimeter Digital Arduino", justify="center", font=ctk.CTkFont('calibri', 32))
    title_label.grid(column=0, row=0, sticky="nsew")

    global Arduino_label
    Arduino_label = ctk.CTkLabel(frame_root, text="Port", font=ctk.CTkFont('calibri', 16))
    Arduino_label.grid(row=1, column=0, sticky="ns", padx=10, pady=10)

    button_frame = ctk.CTkFrame(frame_root)
    button_frame.grid(column=0, row=2, sticky="nsew", padx=10, pady=10)
    button_frame.rowconfigure(0, weight=1)
    button_frame.columnconfigure([0, 1, 2], weight=1)

    global start_stop_button, pause_resume_button, reset_button
    start_stop_button = ctk.CTkButton(button_frame, text="Start", command=toggle_start_stop)
    start_stop_button.grid(row=0, column=0, sticky="nsew", padx=10)
    pause_resume_button = ctk.CTkButton(button_frame, text="Pause", command=toggle_pause_resume, state="disabled")
    pause_resume_button.grid(row=0, column=1, sticky="nsew", padx=10)
    reset_button = ctk.CTkButton(button_frame, text="Reset", command=reset_plot)
    reset_button.grid(row=0, column=2, sticky="nsew", padx=10)

    plot_frame = ctk.CTkFrame(frame_root)
    plot_frame.grid(column=0, row=3, sticky="nsew")
    plot_frame.rowconfigure(0, weight=1)
    plot_frame.columnconfigure(0, weight=1)

    tabview = ctk.CTkTabview(master=plot_frame, height=440)
    tabview.grid(column=0, row=0, sticky="nsew")
    tabview.rowconfigure(0, weight=1)
    tabview.columnconfigure(0, weight=1)
    f0 = tabview.add("Grafik (V,I,R)-t")
    f1 = tabview.add("Grafik V-R")
    f2 = tabview.add("Grafik I-R")
    f3 = tabview.add("Grafik V-I")
    f4 = tabview.add("Data Percobaan")
    # Mengatur isi setiap tab menjadi responsif
    for frame in [f0,f1, f2, f3, f4]:
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

    global fig_all, ax_all, canvas_all
    global fig_ampere, ax_ampere, canvas_ampere, fig_volt, ax_volt, canvas_volt
    global fig_resistance, ax_resistance, canvas_resistance

    fig_all, ax_all, canvas_all = create_plot(f0)
    fig_ampere, ax_ampere, canvas_ampere = create_plot(f1)
    fig_volt, ax_volt, canvas_volt = create_plot(f2)
    fig_resistance, ax_resistance, canvas_resistance = create_plot(f3)
    reset_plot()
    
    frame_table = ctk.CTkFrame(f4)
    frame_table.grid(column=0, row=0, sticky="nsew")
    frame_table.rowconfigure(0, weight=1)
    frame_table.columnconfigure(0, weight=1)
    global table
    table = CTkTable(master=frame_table, values=[columns], header_color="dark blue", width=128, padx=0, row=10,
                     height=10, border_width=1, border_color="black",corner_radius=5)
    table.grid(column=0, row=0, sticky="nsew")

    export_button = ctk.CTkButton(frame_table, text="Ekspor Data", command=export_data)
    export_button.grid(column=0, row=1, sticky="nsew", padx=10, pady=10)

    data_frame = ctk.CTkFrame(frame_root)
    data_frame.grid(column=0, row=4, sticky="nsew", padx=10, pady=10)
    data_frame.rowconfigure(0, weight=1)
    data_frame.columnconfigure(0, weight=1)
    global table_now
    table_now = CTkTable(master=data_frame, values=[columns], header_color="dark blue", width=128, padx=0, row=2)
    table_now.grid(column=0, row=0, sticky="nsew")
    add_button = ctk.CTkButton(data_frame, text="Tambah Data", command=add_data)
    add_button.grid(column=0, row=1, sticky="nsew", padx=10, pady=10)

    connect_to_arduino()
    update_arduino_state()
    root.after(500, plot_multimeter)

def create_plot(tab_name):
    frame = ctk.CTkFrame(tab_name)
    frame.grid(column=0, row=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    fig, ax = plt.subplots(constrained_layout=True)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    # Mengatur canvas agar bisa diresize seperti frame dengan rowconfigure dan columnconfigure
    return fig, ax, canvas

# --- Button Functions ---
def toggle_start_stop():
    global plotting
    plotting = not plotting
    start_stop_button.configure(text="Stop" if plotting else "Start")
    pause_resume_button.configure(state="normal" if plotting else "disabled")

def toggle_pause_resume():
    global paused
    paused = not paused
    pause_resume_button.configure(text="Resume" if paused else "Pause")

# --- Main Program ---
root = ctk.CTk()
root.title("Multimeter Digital Arduino")
root.geometry("500x700")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

frame_root = ctk.CTkFrame(master=root)
frame_root.grid(row=0, column=0, sticky="nsew")
frame_root.rowconfigure([0, 1, 2, 3, 4], weight=1)
frame_root.columnconfigure(0, weight=1)

initialize_gui()
root.mainloop()
