[English](README.md) | [Tiếng Việt](README.vi.md)

# 🚁 Pidron — SITL Swarm Simulator

![Pidron Simulator Banner](asset/IMG_1592.JPG)

> Pidron is a Software-in-the-Loop (SITL) simulator dedicated to the research and development of multi-UAV swarms.

## 🌟 Introduction

Pidron provides a realistic physics environment, a modular autopilot system, a swarm coordination layer, and a web-based 3D visual interface. This project is primarily designed for research, simulation, and testing of UAV control algorithms.

*Disclaimer: Pidron is intended for research and simulation purposes. Do not use it to control real aircraft without passing proper safety validations and Hardware-in-the-Loop testing.*

## ✨ Key Features

*   **Physics Engine:** Runs at 200Hz, modeling motor dynamics, air drag, wind turbulence, and ground interaction.
*   **uORB Bus Architecture:** Pub/sub communication channel for control modules.
*   **Swarm Coordinator:** Handles formation mathematics (e.g., V-Formation), task assignment, and collision avoidance (Artificial Potential Fields).
*   **Web 3D Interface (Web UI):** Uses React and Three.js for real-time visualization of UAVs, flight trajectories, and telemetry data.
*   **Fault Injection:** Supports simulating engine failures, GPS loss, or wind turbulence to test system resilience.
*   **Data Logging & Replay:** Exports telemetry data (in JSON/rosbag-like format) for post-flight review and analysis.

## 🛠 Technologies Used

*   **Backend:** Rust (Handles physics simulation, Flight runtime, Swarm Coordinator, WebSockets API).
*   **Frontend:** TypeScript, React, Three.js, Vite.
*   **Protocol:** Custom JSON WebSockets API (MAVLink is not used by default).

## 🚀 Quickstart

### System Requirements
*   **Rust:** Version 1.70 or higher (Install via `rustup.rs`).
*   **Node.js & pnpm:** Node.js 18+, pnpm 8+.

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourorg/pidron.git
   cd pidron
   ```

2. **Run Backend (Rust):**
   Open terminal 1 and run:
   ```bash
   cargo run --release
   ```
   *The server will listen at `ws://127.0.0.1:8080`.*

3. **Run Frontend (TypeScript):**
   Open terminal 2 and run:
   ```bash
   pnpm install
   pnpm dev
   ```

4. **Access the UI:**
   Open your browser at the address shown in the terminal (usually `http://localhost:5174` or `http://127.0.0.1:8080`).

## 🎮 Basic Usage

1. In the web interface, click **ARM ALL** to arm all UAVs.
2. Click **TAKEOFF ALL**, and all UAVs will automatically take off to the default hover altitude (5m).
3. Select a flight formation (e.g., `V-Formation`) from the bottom control panel and click **APPLY** to see the UAVs move into position.

## 📸 Interface and Simulation (Screenshots)

![Screenshot 1](asset/IMG_1593.JPG)
![Screenshot 2](asset/IMG_1594.JPG)
![Screenshot 3](asset/IMG_1595.JPG)

## 📚 Documentation

For more details on the architecture, module development, and advanced usage guides, please refer to the `doc/` directory:
*   [`doc/TECHNICAL.md`](doc/TECHNICAL.md) - Technical architecture and APIs.
*   [`doc/TUTORIAL.md`](doc/TUTORIAL.md) - Quick simulation scenario guide.
*   [`doc/USER_GUIDE.md`](doc/USER_GUIDE.md) - Detailed usage guide for UI and features.
*   [`doc/DEVELOPER_GUIDE.md`](doc/DEVELOPER_GUIDE.md) - Guide for developers wanting to contribute.

## 🤝 Hardware Partnership

We are actively looking for partners to develop custom hardware specifically for this application. If you are interested in collaboration or hardware integration, please contact us via email: **vietchungvn@gmail.com**.

## 📜 License

Please refer to the `LICENSE` file in the source code.
