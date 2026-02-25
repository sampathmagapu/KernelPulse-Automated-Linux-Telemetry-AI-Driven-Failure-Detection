import time
import os
import csv
import subprocess
import multiprocessing

# =====================================================================
# PART 1: CONFIGURATION & SETUP
# =====================================================================
FILENAME = "hybrid_dataset.csv"
POLL_INTERVAL = 1.0  

# Timeline of the Gauntlet (in seconds)
T_BASELINE_END = 45      # 0 to 45s: You open apps manually
T_CPU_STRESS_END = 75    # 45s to 75s: stress-ng CPU attack
T_RECOVERY_END = 105     # 75s to 105s: System cools down
T_MEM_LEAK_END = 145     # 105s to 145s: Organic Memory Leak bug
T_FINAL_END = 160        # 145s to 160s: Final cleanup

HEADER = ["timestamp", "cpu_user_pct", "cpu_system_pct", "cpu_idle_pct", 
          "context_switches", "available_mem_kb", "major_page_faults", "label"]

# =====================================================================
# PART 2: THE ORGANIC BUG (Memory Leak Method)
# =====================================================================
def organic_memory_leak():
    """This function simulates poorly written software. 
    It creates an infinite loop that constantly hogs RAM and never frees it."""
    junk_data = []
    try:
        while True:
            # Append 20 Megabytes of raw text to the list
            junk_data.append(" " * 20_000_000) 
            time.sleep(0.5) # Slow it down so it doesn't crash the PC instantly
    except KeyboardInterrupt:
        pass

# =====================================================================
# PART 3: SENSORS (Reading the Kernel)
# =====================================================================
def get_cpu_ticks():
    with open("/proc/stat", "r") as f:
        parts = f.readline().split()
        return {"user": int(parts[1]), "system": int(parts[3]), 
                "idle": int(parts[4]), "total": sum(map(int, parts[1:8]))}

def get_context_switches():
    with open("/proc/stat", "r") as f:
        for line in f:
            if line.startswith("ctxt"):
                return int(line.split()[1])
    return 0

def get_available_mem():
    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemAvailable"):
                return int(line.split()[1])
    return 0

def get_page_faults():
    with open("/proc/vmstat", "r") as f:
        for line in f:
            if line.startswith("pgmajfault"):
                return int(line.split()[1])
    return 0

# =====================================================================
# PART 4: THE MAIN EXPERIMENT LOOP
# =====================================================================
if __name__ == "__main__":
    # Create the CSV
    with open(FILENAME, "w", newline='') as f:
        csv.writer(f).writerow(HEADER)

    print("\n🚀 --- STARTING THE HYBRID TELEMETRY GAUNTLET --- 🚀")
    print("Keep your eyes on the terminal. It will tell you when to act!\n")

    # Baseline readings
    prev_cpu = get_cpu_ticks()
    prev_ctxt = get_context_switches()
    prev_faults = get_page_faults()

    start_time = time.time()
    
    # State tracking variables
    cpu_stress_started = False
    mem_leak_process = None

    try:
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # --- PHASE CONTROL & TERMINAL CLUES ---
            if elapsed < T_BASELINE_END:
                label = 0
                msg = "🟢 [NORMAL] Please open Firefox, click around, add some 'Human Noise'!"
            
            elif elapsed < T_CPU_STRESS_END:
                label = 1
                msg = "🔴 [ANOMALY 1] SYNTHETIC CPU STRESS! Please stop moving the mouse."
                if not cpu_stress_started:
                    subprocess.Popen(["stress-ng", "--cpu", "1", "--timeout", "30s"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    cpu_stress_started = True
            
            elif elapsed < T_RECOVERY_END:
                label = 0
                msg = "🟢 [RECOVERY] Close Firefox. Let the system catch its breath."
            
            elif elapsed < T_MEM_LEAK_END:
                label = 2 # Note: Label 2 means a different type of bug!
                msg = "🟠 [ANOMALY 2] ORGANIC MEMORY LEAK! Watch your RAM drop..."
                if mem_leak_process is None:
                    # Start our defective Python function in the background
                    mem_leak_process = multiprocessing.Process(target=organic_memory_leak)
                    mem_leak_process.start()
            
            elif elapsed < T_FINAL_END:
                label = 0
                msg = "🟢 [CLEANUP] Killing the memory leak. Saving final data."
                if mem_leak_process and mem_leak_process.is_alive():
                    mem_leak_process.terminate() # Force kill the bad code
            else:
                print(f"\n✅ Gauntlet Complete! {int(elapsed)} seconds of data saved to {FILENAME}")
                break

            # --- SENSOR RECORDING ---
            time.sleep(POLL_INTERVAL)
            curr_cpu = get_cpu_ticks()
            curr_ctxt = get_context_switches()
            curr_mem = get_available_mem()
            curr_faults = get_page_faults()

            # --- MATH (DELTAS) ---
            delta_total = max(curr_cpu["total"] - prev_cpu["total"], 1)
            user_pct = ((curr_cpu["user"] - prev_cpu["user"]) / delta_total) * 100
            sys_pct = ((curr_cpu["system"] - prev_cpu["system"]) / delta_total) * 100
            idle_pct = ((curr_cpu["idle"] - prev_cpu["idle"]) / delta_total) * 100

            cs_rate = curr_ctxt - prev_ctxt
            fault_rate = curr_faults - prev_faults

            # Save to CSV
            row = [f"{current_time:.2f}", f"{user_pct:.1f}", f"{sys_pct:.1f}", 
                   f"{idle_pct:.1f}", cs_rate, curr_mem, fault_rate, label]
            with open(FILENAME, "a", newline='') as f:
                csv.writer(f).writerow(row)

            # Print to screen so you know what is happening
            print(f"{msg} | CPU: {user_pct+sys_pct:04.1f}% | Mem: {curr_mem}kB | CS/s: {cs_rate}")

            # Update loop variables
            prev_cpu = curr_cpu
            prev_ctxt = curr_ctxt
            prev_faults = curr_faults

    except KeyboardInterrupt:
        if mem_leak_process and mem_leak_process.is_alive():
            mem_leak_process.terminate()
        print("\nAborted safely. Data saved.")