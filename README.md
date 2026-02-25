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
