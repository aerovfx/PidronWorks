# Pipeline Gap Analysis — Pidron vs Real-World Drone Stack

## Overview

This document analyzes the gaps between the current Pidron SITL swarm simulator and a typical real-world drone stack that includes AI/computer vision, companion computer, MAVLink/ROS2, PX4 autopilot, flight controller, ESCs, and motors. The analysis is based on the existing implementation in the `server/` directory (Rust SITL) and the frontend visualization.

## Pipeline Overview

```
AI / Computer Vision          ← NOT IMPLEMENTED
  (YOLO, OpenCV, LLM, SLAM)
        │
  Companion Computer          ← NOT IMPLEMENTED
  (Jetson, RPi, x86)
        │
  MAVLink / MAVSDK / ROS2     ← NOT IMPLEMENTED (internal equivalent)
        │
  PX4 Autopilot Core          ← BUILT IN‑HOUSE (SITL Rust)
        │
  EKF + Flight Control        ← IMPLEMENTED (Complementary Filter instead of EKF)
        │
  Pixhawk Flight Controller   ← NOT IMPLEMENTED (Rust server substitute)
        │
  ESC → Motor → Drone         ← FULLY SIMULATED
```

## Detailed Layer Analysis

### ❌ Layer 1 — AI / Computer Vision (YOLO, OpenCV, LLM, SLAM)

**Status:** NOT IMPLEMENTED

| Feature                | Status |
|------------------------|--------|
| Object Detection (YOLO) | ❌ Absent |
| Camera stream / OpenCV | ❌ Absent |
| SLAM / Mapping         | ❌ Absent |
| LLM mission planning   | ❌ Absent |
| Target tracking        | ❌ Absent |

**Notes:** The current pipeline lacks any camera or computer‑vision input. The Swarm Coordinator relies purely on mathematical formations (APF, formation math) rather than environment perception.

### ❌ Layer 2 — Companion Computer (Jetson, Raspberry Pi, x86)

**Status:** NOT APPLICABLE (simulation‑only)

| Component                     | Status |
|-------------------------------|--------|
| Jetson / RPi hardware abstraction | ❌ Absent |
| ROS2 node pipeline            | ❌ Absent |
| Camera driver → frame capture | ❌ Absent |
| Telemetry forwarding to ground| ❌ Absent (browser substitutes) |

**Notes:** The Rust server running on the host acts as a “virtual companion computer” but provides no ROS2 nodes, driver layers, or hardware interfaces.

### ❌/⚠️ Layer 3 — MAVLink / MAVSDK / ROS2

**Status:** INTERNAL PROTOCOL SUBSTITUTE (JSON over WebSocket)

| Feature               | Status |
|-----------------------|--------|
| MAVLink message format| ❌ Replaced by custom JSON WS |
| MAVSDK wrapper        | ❌ Absent |
| ROS2 topic/publisher  | ❌ Absent |
| HEARTBEAT / param sets| ❌ Absent |

**Internal equivalents implemented:**

| MAVLink equivalent | Pidron implementation |
|--------------------|-----------------------|
| `HEARTBEAT`        | WebSocket `"type":"telemetry"` at 50 Hz |
| `SET_ATTITUDE_TARGET`| JSON `"type":"input"` (pitch/roll/yaw/climb) |
| `COMMAND_LONG` (ARM/TAKEOFF) | JSON `"type":"command"` (cmd) |
| Multi‑vehicle routing| JSON `"type":"select_drone"` + per‑UAV stacks |
| `MISSION_ITEM` waypoints| JSON `"type":"swarm_mission"` |

**Note:** The custom protocol prevents direct connection to standard ground‑station software (QGroundControl, MAVSDK‑based apps).

### ✅ Layer 4 — PX4 Autopilot Core

**Status:** FULLY REIMPLEMENTED IN Rust (SITL)

| PX4 module          | Pidron equivalent | Source file |
|---------------------|-------------------|-------------|
| `uORB` pub/sub bus  | `OrbBus` (`watch::Sender/Receiver`) | `server/uorb.rs` |
| `commander`         | State machine (ARM/TAKEOFF/LAND/EMERGENCY) | `server/modules/commander.rs` |
| `ekf2`              | Complementary Filter (Gyro+Accel+GPS+Baro) | `server/modules/estimator.rs` |
| `mc_pos_control`    | PID position + offboard setpoint | `server/modules/pos_control.rs` |
| `mc_att_control`    | PID attitude (roll/pitch/yaw) | `server/modules/att_control.rs` |
| `mixer`             | Motor mixing matrix (X‑frame quadcopter) | `server/modules/mixer.rs` |
| `px4_simulink_codegen` SITL | Physics engine @ 200 Hz | `server/modules/simulator.rs` |
| Multi‑vehicle swarm | Swarm Coordinator + APF repulsion | `server/modules/swarm_coordinator.rs` |

**PX4‑like features implemented:**
- Flight modes: POSITION / ALTITUDE / STABILIZE
- Offboard position control (setpoint tracking)
- Manual override priority (stick > 0.08 cancels offboard)
- Motor‑failure injection (motor 0 thrust = 0)
- Battery simulation (drain over time)
- State machine: DISARMED → ARMED → TAKEOFF → HOVER → LAND
- Emergency stop for all UAVs

### ✅ Layer 5 — EKF + Flight Control + Navigation

**Status:** IMPLEMENTED (simplified)

| Component          | PX4 (reference) | Pidron implementation | Assessment |
|--------------------|-----------------|----------------------|------------|
| State Estimator    | EKF2            | Complementary Filter | ⚠️ Simpler but sufficient for simulation |
| Attitude control   | Quaternion PID  | Euler‑angle PID      | ⚠️ Gimbal lock at large angles |
| Position control   | Cascade PID + velocity FF | Cascade PID | ✅ Equivalent |
| Navigation         | Waypoint + mission planner | Swarm Coordinator waypoints | ✅ Adequate for swarm |
| Sensor fusion      | IMU+GPS+Baro+Mag| IMU+GPS+Baro         | ⚠️ Missing magnetometer |

### ✅ Layer 6 — Pixhawk Flight Controller (Hardware)

**Status:** REPLACED BY Rust SITL (Software‑in‑the‑Loop)

| Pixhawk hardware | Pidron SITL equivalent |
|------------------|------------------------|
| STM32 MCU @ 400 MHz | Tokio async runtime on host CPU |
| PWM output → ESC | `actuator_outputs` uORB topic (float [0..1]) |
| FMU/IO split     | Single Rust process |
| Hardware failsafe| Software emergency stop |

### ✅ Layer 7 — ESC → Motor → Drone

**Status:** FULLY PHYSICAL SIMULATION

| Component                     | Implementation detail |
|-------------------------------|-----------------------|
| ESC PWM dynamics              | Motor inertia: `lerp(speed, target, dt * 14.0)` |
| Motor thrust model            | `T = motor_speed × max_accel (5.2 m/s²)` |
| X‑frame mixing                | `T0±T1±T2±T3` → roll/pitch/yaw torques |
| Aerodynamic drag              | Relative wind velocity drag |
| Gravity                       | `‑9.81 m/s²` world frame |
| Ground contact                | Bounce suppression + friction |
| Geofence                      | Hard clamp `±60 m × ±60 m` |
| Wind disturbance              | `rx_wind: Vec3` → drag perturbation |
| Motor failure                 | Motor 0 thrust = 0 on failure flag |
| Sensor noise                  | LCG random: Accel ±0.18, Gyro ±0.02, Baro ±0.08, GPS ±0.05 |
| Multi‑UAV                     | 8 independent physics loops @ 200 Hz |

## Summary Table

| Pipeline Layer               | Pidron Status               | Completeness |
|------------------------------|-----------------------------|--------------|
| AI/CV (YOLO/SLAM/LLM)        | ❌ Not implemented          | 0 % |
| Companion Computer           | ❌ Not applicable (sim)     | 0 % |
| MAVLink/MAVSDK/ROS2          | ⚠️ Internal JSON‑WS substitute | 30 % |
| PX4 Autopilot Core           | ✅ Rust SITL reimplementation | 80 % |
| EKF + Flight Control         | ✅ Complementary filter     | 70 % |
| Pixhawk Hardware             | ⚠️ Software‑only substitute | 50 % |
| ESC → Motor → Drone          | ✅ Full physics simulation  | 90 % |
| Frontend 3D Visualization    | ✅ Three.js                 | 95 % |
| Swarm Coordination           | ✅ APF + Formations         | 85 % |

## Roadmap to Close the Gaps

### Near‑Term (Medium Effort)
1. **Adopt MAVLink** – Replace the custom JSON WebSocket with the `mavlink` crate to enable QGroundControl, MAVSDK‑Ros2, and standard ground‑station compatibility.
2. **ROS2 Bridge** – Publish telemetry and accept commands via ROS2 topics to allow integration with perception and planning nodes.

### Long‑Term (High Effort)
3. **Computer Vision Integration** – Add a simulated camera sensor publishing OpenCV‑compatible frames; optionally run YOLO/OpenCV pipelines on a companion‑computer simulation.
4. **SLAM Module** – Build a voxel‑ or point‑cloud‑based map using fused GPS and simulated depth data.
5. **LLM Mission Planner** – Interface with an LLM API (e.g., Gemini, Claude) to convert high‑level mission intents into waypoint sets.
6. **Hardware‑in‑the‑Loop (HITL)** – Connect the Pidron server to a real Pixhawk over UART (or CAN) to test with genuine firmware.
7. **Native PX4 SITL** – Replace the custom Rust SITL with the official `px4_sitl` binary for higher fidelity.

## References
- Source files referenced in the analysis are located under `/Users/dangvietchung/Pidron/server/` (see the file comments in the original analysis for exact paths).
- The frontend visualization resides in `/Users/dangvietchung/Pidron/client/` (Three.js‑based).

---
*Document generated from `plan/pipeline_analysis.md` on 2026‑07‑04.*
