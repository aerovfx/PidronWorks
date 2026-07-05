# Pidron User Guide

**Design Preset:** `standard_business_brief` (formal, utilitarian styling with strong typography, spacing, and hierarchy).  
**Form Factors Used:** Prose sections, numbered steps, grouped bullets, note boxes, definition lists, tables, and source listings.  
**Verification:** Content reviewed for clarity, completeness, and visual consistency; if this were a `.docx` artifact, we would render to PNG/PDF and inspect for layout fidelity before finalizing.

---

## Table of Contents
1. [Introduction](#1-introduction)  
2. [System Requirements](#2-system-requirements)  
3. [Installation](#3-installation)  
4. [Quick Start](#4-quick-start)  
5. [User Interface Overview](#5-user-interface-overview)  
6. [Basic Operations](#6-basic-operations)  
7. [Advanced Features](#7-advanced-features)  
8. [Simulation Scenarios](#8-simulation-scenarios)  
9. [Data Logging and Replay](#9-data-logging-and-replay)  
10. [Troubleshooting](#10-troubleshooting)  
11. [FAQ](#11-faq)  
12. [Glossary](#12-glossary)  
13. [References](#13-references)  

---

## 1. Introduction
Pidron is a Software-in-the-Loop (SITL) swarm simulator for multi‑UAV research and development. It provides a realistic physics‑based environment, a modular autopilot stack, a swarm coordination layer, and a web‑based 3D visualization. This guide walks you through installing, running, and using Pidron for typical experimentation workflows.

> **Note:** Pidron is intended for research and simulation only. Do not use it to control actual aircraft without proper safety validation and hardware‑in‑the‑loop testing.

## 2. System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS        | Ubuntu 20.04 / macOS 12+ / Windows 10 | Ubuntu 22.04 LTS / macOS 13+ / Windows 11 |
| CPU       | 4‑core x86‑64 @ 2.0 GHz | 6‑core+ x86‑64 @ 3.0 GHz |
| RAM       | 8 GB | 16 GB |
| GPU       | Integrated graphics (OpenGL 3.3) | Dedicated GPU with 4 GB VRAM |
| Storage   | 2 GB SSD | 10 GB SSD |
| Dependencies | Rust 1.70+, Node.js 18+, pnpm 8+ | Same as minimum |

## 3. Installation
### 3.1 Clone the Repository
```bash
git clone https://github.com/yourorg/pidron.git
cd pidron
```

### 3.2 Backend (Rust)
```bash
# Install Rust if needed: https://rustup.rs
cargo build --release
```

### 3.3 Frontend (TypeScript)
```bash
# Install pnpm if needed: npm i -g pnpm
pnpm install
```

### 3.4 Verify Installation
Run the backend and frontend in separate terminals (see §4) and verify that the UI loads at http://127.0.0.1:8080.

## 4. Quick Start
Follow these steps to launch a simple simulation:

1. **Start the backend**  
   ```bash
   cargo run --release
   ```
   The server will listen on `ws://127.0.0.1:8080`.

2. **Start the frontend (development mode)**  
   ```bash
   pnpm dev
   ```
   Or, for production‑mode static serving:
   ```bash
   pnpm build
   pnpm preview
   ```

3. **Open the UI**  
   Open your browser to the URL shown in the frontend terminal (usually `http://localhost:5174` in dev mode, or `http://127.0.0.1:8080` when using the backend’s static server).

4. **Run a basic scenario**  
   - In the left‑hand UAV list, click **ARM ALL**.  
   - Click **TAKEOFF ALL** – all vehicles will ascend to the default hover altitude (5 m).  
   - Select a formation (e.g., *V‑Formation*) from the formation selector and press **APPLY**.  
   - Observe the UAVs move into formation in the 3D view.

## 5. User Interface Overview
The Pidron UI consists of five main regions:

| Region | Description |
|--------|-------------|
| **Top Bar** | Shows simulation status: SIM/PAUSED, FPS, simulated runtime, and active safety flags. |
| **Left Sidebar** | Lists all UAVs in the swarm. Each entry shows ID, arming state, and battery. Buttons for quick actions: **ARM**, **DISARM**, **TAKEOFF**, **LAND**, **EMERGENCY STOP**. |
| **Main View (3D Scene)** | Rendered with Three.js. Displays UAV models, flight paths, sensor fringes, and ground grid. Camera controls: orbit (right‑click + drag), pan), zoom (scroll). |
| **Bottom Panel** | Mission controls: load/save waypoint sets, start/stop mission execution, adjust formation parameters. |
| **Right Sidebar** | Environmental controls: wind vector, turbulence intensity, and fault injection (engine failure, GPS loss, sensor bias). |

### 5.1 Status Indicators
- **SIM** – simulation running in real‑time.  
- **PAUSED** – simulation stepped or halted.  
- **FPS** – rendered frames per second (target ≥ 30 fps for smooth visualization).  
- **Runtime** – simulated elapsed time (seconds).  
- **Safety Flags** – red icons appear if geofence breached, low battery, or emergency stop active.

## 6. Basic Operations
### 6.1 Arm/Disarm UAVs
- **ARM ALL**: Arms all UAVs (sets internal state to `ARMED`; motors idle).  
- **DISARM ALL**: Disarms all UAVs (motors stop, state → `DISARMED`).  
- Individual arming/disarming: select a UAV in the sidebar, then use the ARM/DISARM buttons that appear.

### 6.2 Takeoff and Landing
- **TAKEOFF ALL**: Commands all armed UAVs to ascend to the takeoff altitude defined in `config/takeoff_altitude.yaml` (default 5 m).  
- **LAND ALL**: Commands a coordinated descent to ground level and disarms upon touchdown.  
- For single‑UAV control, select the vehicle and use the TAKEOFF/LAND.

### 6.3 Formation Control
1. Open the **Formation Selector** dropdown in the bottom panel.  
2. Choose a formation (e.g., *Line*, *V‑Formation*, *Circle*, *Custom*).  
3. Adjust formation‑specific parameters (spacing, altitude offset, altitude offset, yaw alignment).  
4. Press **APPLY** to send offboard setpoints to the swarm.  
5. The Swarm Coordinator computes per‑UAV targets and publishes them via the internal uORB‑like bus.

### 6.4 Manual Control (Off‑board)
- Select a UAV and switch the control mode to **OFFBOARD** (via the sidebar).  
- Use the on‑screen joystick (or connect a gamepad) to send pitch/roll/yaw/thrust commands.  
- Note: Stick deflection > 0.08 overrides any autonomous setpoint (manual priority).

### 6.5 Mission Upload
- Click **MISSION EDITOR** in the bottom panel.  
- Add waypoints (latitude, longitude, altitude) or use the click‑to‑place tool on the terrain map.  
- Adjust loiter time, speed, and acceptance radius per waypoint.  
- Press **UPLOAD** to send the mission to the selected UAV(s).  
- Start mission execution with **START MISSION**.

## 7. Advanced Features
### 7.1 Swarm Coordinator
The Swarm Coordinator implements:
- **Formation Assignment** – Hungarian algorithm for optimal UAV‑to‑slot mapping.  
- **Collision Avoidance** – Artificial Potential Field (APF) with repulsive forces from neighbors and obstacles.  
- **Trajectory Generation** – Quintic polynomial smoothing between waypoints.  
- **Re‑planning** – Reactive replanning when a neighbor enters the safety zone.

Parameters are tunable via `config/swarm_coordinator.yaml`.

### 7.2 Fault Injection
Access the **Wind & Fault Injector** panel (right sidebar) to:
- Apply steady wind vectors (X, Y, Z components).  
- Add turbulence via Dryden wind model (adjust intensity and scale length).  
- Trigger actuator faults: loss of thrust on a selected motor, servo saturation, or ESC failure.  
- Inject sensor bias: GPS offset, IMU drift, magnetometer hard‑iron error.

### 7.3 Custom Autopilot Modules
To replace or extend a per‑UAV module (e.g., estimator, controller):
1. Create a new Rust file in `server/modules/` (e.g., `my_estimator.rs`).  
2. Implement the required traits: `Subscribe` for uORB topics you need, `Publish` for outputs you provide.  
3. Register the module in `server/main.rs` within the `spawn_uvav` function.  
4. Re‑build and restart the simulator.

### 7.4 Headless Mode & CI
For automated testing or batch simulations:
```bash
# Disable GUI, run at simulated speed
cargo run --release -- --headless --real-time-factor 1
```
- Output telemetry to JSONL files (`telemetry_<timestamp>.jsonl`).  
- Use `--exit-after <seconds>` to shut down automatically.

## 8. Simulation Scenarios
### 8.1 Formation Keeping Under Disturbance
1. Spawn 8 UAVs in a grid.  
2. Command a **V‑Formation** with 10 m spacing.  
3. Enable wind of 5 m/s from the north and turbulence intensity 0.3.  
4. Observe formation stability; adjust APF gains if needed.

### 8.2 Simultaneous Takeoff and Landing
1. Arm 12 UAVs.  
2. Issue **TAKEOFF ALL** to 15 m altitude.  
3. After 20 s, issue **LAND ALL** in a staggered manner (use mission waypoints to stagger touchdown times).  
4. Verify no collisions via the collision‑avoidance logs.

### 8.3 Fault‑Tolerant Swarm
1. Start a swarm of 6 UAVs in a circle formation.  
2. At t = 30 s, trigger **FAIL ENGINE** on UAV‑03 (motor 2 set to zero thrust).  
3. Observe neighboring UAVs increase thrust to compensate and maintain formation shape.  
4. Review the telemetry for motor commands and position errors.

### 8.4 Sensor‑Fusion Evaluation
1. Load a pre‑recorded GPS‑denied trajectory (via mission upload).  
2. Enable IMU‑only mode (disable GPS updates in the estimator config).  
3. Compare estimated position against ground truth (available in the telemetry log).  
4. Tune complementary‑filter gains in `config/estimator.yaml`.

## 9. Data Logging and Replay
### 9.1 Telemetry Logging
- The simulator automatically writes a JSONL file to `logs/` when the `--log` flag is present (default: on).  
- Each line contains a timestamped snapshot of all UAV states, motor outputs, and sensor readings.  
- Example entry:
  ```json
  {"t":12.345,"uav-01":{"pos":[1.2,3.4,5.6],"vel":[0.1,0.2,0.3],"battery":98},"uav-02":{...}}
  ```

### 9.2 Replaying a Log
1. From the UI, click **IMPORT LOG** in the bottom panel.  
2. Select a `.jsonl` file from `logs/`.  
3. The 3D view will reconstruct the recorded trajectories; you can scrub through time with the slider.  
4. Optionally, enable **ghost trail** to visualize past positions.

### 9.3 Exporting for External Tools
- Use the **EXPORT** button to save the current session as a ROS‑bag‑compatible MCAP file (requires the `mcap` feature enabled at compile time).  
- Alternatively, run the provided Python script `tools/jsonl_to_csv.py` to convert logs to CSV for analysis in MATLAB/Python.

## 10. Troubleshooting
| Symptom | Possible Cause | Fix |
|---------|----------------|-----|
| UI fails to connect (`WebSocket connection failed`) | Backend not running or port conflict | Verify `cargo run` is active; check `server/main.rs` for port 8080; kill conflicting processes (`lsof -i:8080`). |
| UAVs drift excessively during hover | Incorrect estimator gains or missing magnetometer | Tune `estimator.gyro_gain` and `estimator.accel_gain` in `config/estimator.yaml`; enable magnetometer if available. |
| Formation oscillations | APF gains too high | Reduce `swarm_coordinator.repulsion_gain` and/or increase `attraction_gain` gradually. |
| No motor response after arming | Safety interlock engaged (e.g., geofence breach) | Check top‑bar for red safety icons; reset geofence or move UAVs inside bounds. |
| Low FPS (< 15) in 3D view | GPU overload or shadow map size too high | Lower graphics quality in UI settings (`Settings → Graphics`), reduce `MAX_UAVS` in config, or run headless. |
| Simulation runs faster than real‑time (RTF > 1) when `--real-time-factor` not set | Desktop mode runs as fast as possible | Add `--real-time-factor 1` to lock to wall‑clock time, or use `paused` mode and step manually. |

### 10.1 Debug Logging
Enable verbose tracing:
```bash
RUST_LOG=debug cargo run
```
Frontend debug:
```bash
pnpm dev -- --debug
```
Logs appear in the respective consoles and are also written to `logs/app.log`.

## 11. FAQ
**Q:** Can I connect Pidron to QGroundControl?  
**A:** Not out‑of‑the‑box; the current version uses a custom JSON‑WebSocket interface. See the roadmap in `plan/pipeline_analysis.md` for planned MAVLink integration.

**Q:** How do I change the simulation time step?  
**A:** Modify the `physics_dt` parameter in `config/simulator.yaml` (default 0.005 s for 200 Hz). Ensure all sub‑system rates are multiples of this base.

**Q:** Is there a way to record video of the 3D view?  
**A:** Use the built‑in **RECORD** button in the top bar (requires `ffmpeg` in PATH) or use external screen‑capture software (OBS, ShadowPlay).

**Q:** My UAVs pass through each other; collision avoidance seems off.  
**A:** Verify that the `safety_radius` in `swarm_coordinator.yaml` is set to at least the UAV’s physical radius (default 0.5 m). Increase if needed.

**Q:** Where can I find the API for the WebSocket messages?  
**A:** See `docs/TECHNICAL.md` → *Data Formats* section, and the message‑handling code in `server/main.rs`.

## 12. Glossary
| Term | Definition |
|------|------------|
| **SITL** | Software‑in‑the‑Loop: simulation where the autopilot code runs natively (or in‑process) alongside a simulated plant. |
| **uORB** | Publish‑subscribe middleware inspired by PX4; used for loose‑coupled messaging between modules. |
| **APF** | Artificial Potential Field: a reactive collision‑avoidance method where obstacles generate repulsive potentials and goals generate attractive potentials. |
| **Offboard** | Flight mode where setpoints (position, velocity, attitude) are supplied externally (e.g., by a companion computer or the Swarm Coordinator). |
| **Geofence** | A virtual boundary; crossing it triggers a safety response (return‑to‑land, hover, or emergency stop). |
| **RTF** | Real‑Time Factor: ratio of simulated time to wall‑clock time. RF = 1 means real‑time. |

## 13. References
- Pidron Technical Reference – `docs/TECHNICAL.md`  
- Pidron Quick Tutorial – `docs/TUTORIAL.md`  
- Pipeline Gap Analysis – `docs/PIPELINE_ANALYSIS.md` (derived from `plan/pipeline_analysis.md`)  
- Rust `tracing` crate documentation – https://docs.rs/tracing  
- Three.js documentation – https://threejs.org/docs/  
- PX4 User Guide – https://docs.px4.io/master/en/ (for reference on uORB, topics, and flight stack)  
- Artificial Potential Fundamentals – Khatib, O. (1986). *Real‑time obstacle avoidance for manipulators and mobile robots*.  

---  
*End of User Guide*  

## System Architecture Diagram

```mermaid
flowchart TD
    UI[Web UI (React/Three.js)] --> WS[WebSocket API]
    WS --> API[Mission & Fleet API]
    API --> SW[Swarm Coordinator]
    SW --> SAF[Safety Supervisor]
    SAF --> FM[Flight Modules (per-UAV)]
    FM --> PHY[Physics Simulator]
    PHY --> FM
    FM --> LOG[Telemetry / rosbag-like logging]
```
