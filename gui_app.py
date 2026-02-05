import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import os
import sys

# --- 1. CONFIGURATION: LOAD THE C LIBRARY ---
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_name = "scheduler_lib.dll" if os.name == 'nt' else "scheduler_lib.so"
lib_path = os.path.join(current_dir, lib_name)

try:
    if not os.path.exists(lib_path):
        if os.path.exists(lib_name):
            lib_path = lib_name
        else:
            raise FileNotFoundError(f"Library file not found at: {lib_path}")
            
    scheduler_lib = ctypes.CDLL(lib_path)
except Exception as e:
    messagebox.showerror("Setup Error", f"Could not load C Library.\n\nError: {e}\n\nMake sure you compiled the C code: gcc -shared -o {lib_name} -fPIC scheduler_lib.c")
    sys.exit()

# --- 2. DEFINE C STRUCTURE IN PYTHON ---
class Process(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 10),
        ("arrival_time", ctypes.c_int),
        ("burst_time", ctypes.c_int),
        ("remaining_time", ctypes.c_int),
        ("waiting_time", ctypes.c_int),
        ("turnaround_time", ctypes.c_int),
        ("completion_time", ctypes.c_int),
        ("is_completed", ctypes.c_int)
    ]

# --- 3. GUI APPLICATION CLASS ---
class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Process Scheduling Simulator")
        self.root.geometry("800x650") # Slightly taller to fit footer
        self.processes = [] 

        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Helvetica", 10, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground="#2c3e50")

        # --- UI LAYOUT ---

        # 0. Title Header
        title_frame = ttk.Frame(root)
        title_frame.pack(fill="x", pady=10)
        ttk.Label(title_frame, text="CPU Scheduling Simulator", style="Header.TLabel").pack()

        # 1. Input Section
        input_frame = ttk.LabelFrame(root, text="Add Process", padding=(10, 5))
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, text="Process Name:").grid(row=0, column=0, padx=5)
        self.name_entry = ttk.Entry(input_frame, width=10)
        self.name_entry.grid(row=0, column=1)
        self.name_entry.insert(0, "P1")

        ttk.Label(input_frame, text="Arrival Time:").grid(row=0, column=2, padx=5)
        self.at_entry = ttk.Entry(input_frame, width=10)
        self.at_entry.grid(row=0, column=3)
        self.at_entry.insert(0, "0")

        ttk.Label(input_frame, text="Burst Time:").grid(row=0, column=4, padx=5)
        self.bt_entry = ttk.Entry(input_frame, width=10)
        self.bt_entry.grid(row=0, column=5)
        self.bt_entry.insert(0, "5")

        ttk.Button(input_frame, text="Add", command=self.add_process).grid(row=0, column=6, padx=10)
        ttk.Button(input_frame, text="Clear All", command=self.clear_data).grid(row=0, column=7)

        # 2. Algorithm Controls
        ctrl_frame = ttk.LabelFrame(root, text="Simulation Controls", padding=(10, 5))
        ctrl_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(ctrl_frame, text="Select Algorithm:", style="Bold.TLabel").pack(side="left")
        
        self.algo_var = tk.StringVar(value="FCFS")
        algos = ["FCFS", "SJF (Non-Preemptive)", "SRTF (Preemptive)", "Round Robin"]
        self.algo_combo = ttk.Combobox(ctrl_frame, textvariable=self.algo_var, values=algos, state="readonly", width=25)
        self.algo_combo.pack(side="left", padx=5)
        self.algo_combo.bind("<<ComboboxSelected>>", self.toggle_quantum)

        ttk.Label(ctrl_frame, text="Time Quantum (RR):").pack(side="left", padx=(15, 5))
        self.q_entry = ttk.Entry(ctrl_frame, width=5)
        self.q_entry.pack(side="left")
        self.q_entry.insert(0, "2")
        self.q_entry.config(state="disabled")

        ttk.Button(ctrl_frame, text="▶ RUN SIMULATION", command=self.run_simulation).pack(side="right", padx=10)

        # 3. Results Table
        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        cols = ("Name", "Arrival", "Burst", "Finish", "Turnaround", "Waiting")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
            
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 4. Stats & Gantt
        self.stats_lbl = ttk.Label(root, text="Avg Waiting Time: 0.00  |  Avg Turnaround Time: 0.00", font=("Helvetica", 11, "bold"), foreground="#007acc")
        self.stats_lbl.pack(pady=5)

        self.canvas = tk.Canvas(root, bg="white", height=120)
        self.canvas.pack(fill="x", padx=10, pady=5)
        
        # --- FOOTER CREDITS ---
        footer_frame = ttk.Frame(root)
        footer_frame.pack(side="bottom", fill="x", pady=(0, 10))
        
        tk.Frame(footer_frame, height=1, bg="grey").pack(fill="x", padx=20, pady=5) # Separator line
        
        lbl_name = ttk.Label(footer_frame, text="Developed by: Raiyan Jahan", font=("Segoe UI", 9, "bold"), foreground="#555")
        lbl_name.pack()
        
        lbl_uni = ttk.Label(footer_frame, text="Daffodil International University", font=("Segoe UI", 9), foreground="#777")
        lbl_uni.pack()

        self.toggle_quantum()

    def toggle_quantum(self, event=None):
        if self.algo_var.get() == "Round Robin":
            self.q_entry.config(state="normal")
        else:
            self.q_entry.config(state="disabled")

    def add_process(self):
        try:
            name = self.name_entry.get()
            if not name: raise ValueError("Name required")
            at = int(self.at_entry.get())
            bt = int(self.bt_entry.get())
            
            self.processes.append({"name": name, "at": at, "bt": bt})
            self.update_tree_preview()
            
            try:
                curr_num = int(''.join(filter(str.isdigit, name)))
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, f"P{curr_num + 1}")
            except:
                pass
                
        except ValueError:
            messagebox.showerror("Input Error", "Arrival and Burst Time must be valid integers.")

    def clear_data(self):
        self.processes = []
        self.update_tree_preview()
        self.canvas.delete("all")
        self.stats_lbl.config(text="Avg Waiting Time: 0.00  |  Avg Turnaround Time: 0.00")

    def update_tree_preview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in self.processes:
            self.tree.insert("", "end", values=(p['name'], p['at'], p['bt'], "-", "-", "-"))

    def run_simulation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "Please add at least one process.")
            return

        n = len(self.processes)
        ProcessArray = Process * n
        c_data = ProcessArray()

        for i, p in enumerate(self.processes):
            c_data[i].name = p['name'].encode('utf-8')
            c_data[i].arrival_time = p['at']
            c_data[i].burst_time = p['bt']
            c_data[i].remaining_time = p['bt'] 
            c_data[i].is_completed = 0

        algo = self.algo_var.get()
        
        try:
            if algo == "FCFS":
                scheduler_lib.calculate_fcfs(c_data, n)
            elif algo == "SJF (Non-Preemptive)":
                if not hasattr(scheduler_lib, 'calculate_sjf'):
                     raise AttributeError("function 'calculate_sjf' not found. Please recompile C code.")
                scheduler_lib.calculate_sjf(c_data, n)
            elif algo == "SRTF (Preemptive)":
                if not hasattr(scheduler_lib, 'calculate_srtf'):
                     raise AttributeError("function 'calculate_srtf' not found. Please recompile C code.")
                scheduler_lib.calculate_srtf(c_data, n)
            elif algo == "Round Robin":
                try:
                    quantum = int(self.q_entry.get())
                    if quantum <= 0: raise ValueError
                    scheduler_lib.calculate_round_robin(c_data, n, quantum)
                except ValueError:
                    messagebox.showerror("Error", "Quantum must be a positive integer.")
                    return
        except AttributeError as e:
            messagebox.showerror("Compile Error", f"{e}\n\nIt seems your DLL is outdated.")
            return

        self.display_results(c_data, n)
        self.draw_gantt(c_data, n)

    def display_results(self, c_data, n):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        total_wt = 0
        total_tat = 0
        
        for i in range(n):
            p = c_data[i]
            self.tree.insert("", "end", values=(
                p.name.decode('utf-8'),
                p.arrival_time,
                p.burst_time,
                p.completion_time,
                p.turnaround_time,
                p.waiting_time
            ))
            total_wt += p.waiting_time
            total_tat += p.turnaround_time

        avg_wt = total_wt / n
        avg_tat = total_tat / n
        self.stats_lbl.config(text=f"Avg Waiting Time: {avg_wt:.2f}  |  Avg Turnaround Time: {avg_tat:.2f}")

    def draw_gantt(self, c_data, n):
        self.canvas.delete("all")
        
        # Sort DESCENDING to layer shorter blocks on top of longer ones for visibility
        sorted_procs = sorted([c_data[i] for i in range(n)], key=lambda x: x.completion_time, reverse=True)
        
        if not sorted_procs: return

        max_time = sorted_procs[0].completion_time
        if max_time == 0: max_time = 1
        
        c_width = 750
        start_x = 20
        y = 50
        h = 40
        available_width = c_width - 40
        scale = available_width / max_time

        self.canvas.create_line(start_x, y+h, start_x + max_time*scale, y+h, width=2)
        self.canvas.create_text(start_x, y+h+15, text="0")

        colors = ["#add8e6", "#90ee90", "#ffb6c1", "#f0e68c", "#dda0dd", "#e0ffff"]

        for i, p in enumerate(sorted_procs):
            width = p.burst_time * scale
            end_pixel = start_x + (p.completion_time * scale)
            current_start_pixel = end_pixel - width
            
            color = colors[i % len(colors)]

            self.canvas.create_rectangle(current_start_pixel, y, end_pixel, y+h, fill=color, outline="black")
            
            center_x = (current_start_pixel + end_pixel)/2
            if width > 20: 
                self.canvas.create_text(center_x, y+h/2, text=p.name.decode('utf-8'))
            
            self.canvas.create_text(end_pixel, y+h+15, text=str(p.completion_time))

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()