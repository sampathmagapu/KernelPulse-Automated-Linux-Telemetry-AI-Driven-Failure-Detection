# 🚀 KernelPulse

**KernelPulse** is a lightweight Linux kernel telemetry and anomaly detection pipeline that detects and classifies system-level bottlenecks such as CPU starvation and memory pressure using time-series Machine Learning.

It bridges Linux kernel internals (`/proc`, `/sys`) with structured ML-based diagnostics.

---

## 📌 Problem Statement

Modern systems rarely fail catastrophically.  
Instead, they degrade silently.

Examples:

- CPU throttles under sustained load.
- Memory pressure causes swap thrashing.
- Context switching increases due to scheduler saturation.
- Software memory leaks gradually consume RAM.

These “grey failures” do not crash the system — they silently destroy performance.

KernelPulse detects and diagnoses such degradations automatically.

---

## 🏗 System Architecture

```

Kernel → Telemetry Collector → Feature Pipeline → ML Engine → Diagnostic Report

```

---

## 🧠 Pillar 1: Telemetry Sensor (Linux Kernel Interface)

The system directly reads from:

- `/proc/stat`
- `/proc/meminfo`
- `/proc/vmstat`
- `/proc/loadavg`
- `/sys/devices/system/cpu/...`

No third-party monitoring libraries are used.

### Delta-Based Measurement Logic

Kernel counters are cumulative since boot.

To compute real-time rates:

1. Take snapshot A at time T
2. Take snapshot B at time T+1s
3. Compute delta
4. Normalize into percentages or per-second metrics

Example outputs:
- Context switches per second
- CPU utilization (user/system/idle %)
- Major page faults per second

---

## 📊 Metrics Collected

| Category | Metrics |
|----------|---------|
| CPU | User %, System %, Idle %, Context Switches/sec |
| Load | Load Average (1,5,15 min) |
| Memory | MemAvailable, SwapUsed |
| Memory Pressure | Major Page Faults |
| Frequency | CPU Scaling Frequency |
| Thermal | CPU Temperature (bare-metal mode) |

---

## ⚙️ Pillar 2: Chaos Gauntlet (Dataset Generation)

To train and validate anomaly detection, controlled stress scenarios are created.

### CPU Starvation

```

stress-ng --cpu 4 --timeout 120s

```

Simulates heavy CPU load.

---

### Memory Leak Simulation

A Python process continuously allocates memory without releasing it.

Simulates:
- Real-world RAM leaks
- Gradual degradation
- Swap pressure

---

### Automated Labeling

Data is labeled during experiments:

- 0 → Normal
- 1 → CPU Stress
- 2 → Memory Leak

Produces structured datasets suitable for ML.

---

## 🤖 Pillar 3: Diagnostic Engine (Machine Learning)

### Feature Engineering

Sliding window statistics:
- Mean
- Standard deviation
- Rate of change
- Rolling variance

---

### Anomaly Detection

Algorithm:
- Isolation Forest

Purpose:
- Identify deviation from baseline system behavior.

---

### Output

Generates a PDF diagnostic report including:

- Time-series plots
- Resource utilization graphs
- State distribution
- Written anomaly summary

---

## 🛠 Technical Stack

| Layer | Tools |
|-------|------|
| Language | Python 3 |
| OS | Ubuntu Linux |
| Data | Pandas |
| ML | Scikit-learn |
| Visualization | Matplotlib |
| Stress Tool | stress-ng |
| Environment | VMware (Dev), Bare Metal (Target) |

---

## 📂 Repository Structure

```

kernelpulse/
│
├── collector/
│   └── collector.py
│
├── analyzer/
│   └── analyze.py
│
├── experiments/
│   ├── cpu_stress.sh
│   ├── memory_leak.py
│
├── reports/
│   └── sample_report.pdf
│
└── README.md

```

---

## ▶️ How to Run

### 1️⃣ Start Collector

```

python3 collector.py

```

---

### 2️⃣ Trigger Stress Scenario

CPU:

```

stress-ng --cpu 4 --timeout 60

```

Memory Leak:

```

python3 memory_leak.py

```

---

### 3️⃣ Stop Collector

Press `Ctrl + C`

---

### 4️⃣ Run Analyzer

```

python3 analyze.py hardware_data.csv

```

---

## 🧩 Engineering Challenges

### CPU Delta Computation

`/proc/stat` provides cumulative tick counters.

Correct calculation requires:
- Storing previous totals
- Computing delta
- Normalizing by total tick difference

Incorrect handling results in inaccurate CPU metrics.

---

### Memory Leak Isolation

Naively allocating memory blocks the main telemetry loop.

Solution:
- Use `multiprocessing`
- Spawn separate process
- Prevent collector from freezing

---

### VM vs Bare Metal Behavior

In VMware:
- CPU temperature may not be exposed.
- Frequency scaling differs.

Collector handles missing hardware gracefully.

---

## 📈 Performance Characteristics

- Sampling Rate: 1 Hz
- CPU Overhead: < 2%
- Memory Footprint: < 30 MB
- Log Rotation Supported

---

## 🎯 Why This Project Matters

KernelPulse demonstrates:

- Deep Linux internals knowledge
- Controlled experiment design
- Kernel-level telemetry engineering
- Time-series anomaly detection
- End-to-end system thinking

Targets performance engineering and validation roles in:

- Semiconductor companies
- Data center infrastructure teams
- Systems software engineering teams

---

- Integrate hardware perf counters
- Add LSTM-based sequence modeling
- Real-time anomaly alerts
- Prometheus exporter
- Cross-CPU comparison experiments
```
