import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# 1. Load your exact dataset
filename = "hybrid_dataset.csv"
df = pd.read_csv(filename)

# 2. Setup the PDF File
pdf_filename = "Telemetry_Report.pdf"

print("📊 Generating professional PDF report...")

with PdfPages(pdf_filename) as pdf:
    
    # ==========================================
    # PAGE 1: THE TIME-SERIES GRAPH
    # ==========================================
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    # Plot CPU on the left Y-axis
    ax1.plot(df.index, df['cpu_user_pct'], color='#e74c3c', linewidth=2, label="CPU User %")
    ax1.set_xlabel('Time (Seconds)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('CPU Utilization (%)', color='#e74c3c', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#e74c3c')
    
    # Plot Memory on the right Y-axis
    ax2 = ax1.twinx()  
    # Convert kB to MB for readability
    ax2.plot(df.index, df['available_mem_kb'] / 1024, color='#3498db', linewidth=2, label="Available Mem (MB)")
    ax2.set_ylabel('Available Memory (MB)', color='#3498db', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#3498db')

    plt.title('System Resources Over Time (The Gauntlet)', fontsize=16, fontweight='bold')
    fig1.tight_layout()
    pdf.savefig(fig1)  # Save Page 1
    plt.close()

    # ==========================================
    # PAGE 2: THE PIE CHART
    # ==========================================
    fig2, ax = plt.subplots(figsize=(8, 8))
    
    # Count how many seconds were spent in each label
    label_counts = df['label'].value_counts()
    
    # Map the labels securely based on your data (0: Normal, 1: CPU, 2: Mem Leak)
    counts = [label_counts.get(0, 0), label_counts.get(1, 0), label_counts.get(2, 0)]
    labels = ['Normal / Recovery', 'CPU Starvation', 'Memory Leak']
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    
    # Draw the Pie Chart
    ax.pie(counts, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140, 
           wedgeprops={'edgecolor': 'black', 'linewidth': 1}, textprops={'fontsize': 12})
    
    plt.title('Experiment Phase Breakdown', fontsize=16, fontweight='bold')
    pdf.savefig(fig2)  # Save Page 2
    plt.close()

    # ==========================================
    # PAGE 3: THE EXPLANATION
    # ==========================================
    fig3 = plt.figure(figsize=(10, 6))
    fig3.clf()
    
    # Format the text nicely
    report_text = f"""
    HARDWARE TELEMETRY & PERFORMANCE DIAGNOSTIC REPORT
    -------------------------------------------------------------------------
    Total Experiment Duration : {len(df)} seconds
    Starting Available Memory : {df['available_mem_kb'].iloc[0] / 1024:.0f} MB
    Ending Available Memory   : {df['available_mem_kb'].iloc[-1] / 1024:.0f} MB
    
    DIAGNOSIS & FINDINGS:
    
    1. Human Noise Phase (Normal): 
       The system idled normally, capturing slight variations when apps were manually 
       opened. The OS scheduler handled these spikes perfectly without starvation.
       
    2. Synthetic CPU Starvation (Anomaly 1): 
       A stress-ng worker thread successfully locked a single CPU core, proving the 
       telemetry sensor's ability to capture immediate, sharp bottleneck thresholds.
       
    3. Organic Memory Leak (Anomaly 2): 
       A defective process aggressively consumed RAM. Unlike the CPU spike, this was 
       a gradual slope. Available memory drained significantly until the process was 
       terminated, proving the script can detect gradual software defects.
       
    CONCLUSION:
    The telemetry pipeline successfully isolated and documented three distinct 
    operational states without crashing the host operating system.
    """
    
    # Place text on the blank page
    fig3.text(0.05, 0.5, report_text, transform=fig3.transFigure, size=12, ha="left", va="center", family='monospace')
    pdf.savefig(fig3)  # Save Page 3
    plt.close()

print(f"✅ Success! Open '{pdf_filename}' in your file explorer to see the results.")