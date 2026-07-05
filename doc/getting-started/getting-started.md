# Pidron — Getting Started Guide

This guide provides a comprehensive introduction to getting started with Pidron, including installation, basic usage, and common workflows for new users.

## Table of Contents
1. [Overview](#1-overview)
2. [System Requirements](#2-system-requirements)
3. [Installation](#3-installation)
4. [Quick Start](#4-quick-start)
5. [Running the Simulation](#5-running-the-simulation)
6. [Using the Web Interface](#6-using-the-web-interface)
7. [Basic Workflows](#7-basic-workflows)
8. [Configuration](#8-configuration)
9. [Troubleshooting](#9-troubleshooting)
10. [Next Steps](#10-next-steps)

## 1. Overview

Pidron is a Software-in-the-Loop (SITL) swarm simulator for multi-UAV research and development. It provides:
- A realistic physics-based environment
- A modular autopilot stack (estimator, controller, mixer)
- A swarm coordination layer
- A web-based 3D visualization interface
- Support for hardware-in-the-loop (HITL) scenarios

The simulator consists of two main components:
- **Backend (Server)**: Rust-based simulation engine with WebSocket API
- **Frontend (Client)**: TypeScript/React-based web interface with Three.js rendering

## 2. System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10
- **CPU**: Modern x86_64 processor with at least 2 cores
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB available space
- **Graphics**: GPU with OpenGL 3.3+ support for 3D visualization

### Software Dependencies
- **Rust**: 1.65+ (installed via rustup)
- **Node.js**: 16.x or 18.x
- **Package Manager**: pnpm (recommended) or npm/yarn
- **Git**: For cloning the repository

## 3. Installation

### 3.1 Clone the Repository
```bash
git clone https://github.com/aerovfx/pidron.git
cd pidron
```

### 3.2 Install Backend Dependencies (Rust)
The Rust toolchain is required to build the simulation backend.

#### Using rustup (recommended):
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustup update stable
```

#### Verify Installation:
```bash
rustc --version
cargo --version
```

### 3.3 Install Frontend Dependencies (Node.js)
#### Using Node Version Manager (nvm):
```bash
# Install nvm (if not already installed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install and use Node.js 18
nvm install 18
nvm use 18
```

#### Install pnpm:
```bash
npm install -g pnpm
```

### 3.4 Install Project Dependencies
```bash
# Install backend dependencies
cargo fetch

# Install frontend dependencies
pnpm install
# or: npm install
```

## 4. Quick Start

For those who just want to get up and running quickly:

```bash
# Build the backend (release mode for better performance)
cargo build --release

# Install frontend dependencies (if not done already)
pnpm install

# Start the backend in one terminal:
cargo run --release

# Start the frontend in another terminal:
pnpm dev

# Open your browser to:
# http://127.0.0.1:8080 (production build)
# or the Vite dev server URL (typically http://localhost:5174)
```

## 5. Running the Simulation

### 5.1 Backend Server Modes
The backend can be run in different modes depending on your needs:

#### Debug Mode (for development):
```bash
cargo run
```
Features:
- Faster compilation
- Debug assertions enabled
- More verbose logging
- Slower simulation speed

#### Release Mode (for performance testing):
```bash
cargo run --release
```
Features:
- Optimized compilation
- Maximum simulation speed
- Reduced logging overhead

#### With Logging:
```bash
# Control log level with RUST_LOG
RUST_LOG=info cargo run --release
RUST_LOG=debug cargo run --release
RUST_LOG=trace cargo run --release
```

#### With Features:
```bash
# Enable MCAP logging feature
cargo run --release --features mcap
```

### 5.2 Frontend Development Modes
The frontend can be run in different modes:

#### Development Mode (with hot reload):
```bash
pnpm dev
# or: npm run dev
```
Features:
- Automatic recompilation on file changes
- Source maps for debugging
- Not optimized for performance

#### Production Build:
```bash
pnpm build
# or: npm run build
```
Features:
- Optimized bundle
- Minified assets
- Ready for deployment

#### Preview Production Build:
```bash
pnpm preview
# or: npm run preview
```
Features:
- Serves the built production bundle locally
- Useful for testing production build

## 6. Using the Web Interface

Once both backend and frontend are running, open your browser to the displayed URL (typically http://localhost:5174 for dev or http://127.0.0.1:8080 for production).

### 6.1 Interface Overview
- **Top Bar**: Shows simulation status (SIM/PAUSED), FPS, and runtime statistics
- **Left Sidebar**: UAV management panel (list of UAVs, arming, takeoff, landing controls)
- **Main View**: 3D visualization window showing UAVs, terrain, and flight paths
- **Bottom Panel**: Mission controls, formation editor, and waypoint management
- **Right Panel**: Environmental controls (wind, gravity) and fault injection tools

### 6.2 Basic Controls
- **Mouse Orbit**: Right-click + drag to rotate camera around focal point
- **Mouse Pan**: Middle-click + drag or Shift + left-click + drag to pan view
- **Mouse Scroll**: Zoom in/out
- **Keyboard**: 
  - `R`: Reset camera to default position
  - `F`: Focus on selected UAV
  - `Space`: Pause/resume simulation

### 6.3 UAV Management
Each UAV in the left sidebar shows:
- **ID**: Unique identifier (e.g., uav-01, uav-02)
- **Status**: DISARMED, ARMED, FLYING, etc.
- **Battery**: Current charge level (%)
- **Controls**: ARM, DISARM, TAKEOFF, LAND, EMERGENCY STOP buttons

## 7. Basic Workflows

### 7.1 Single UAV Takeoff and Landing
1. Ensure the simulator is running and the 3D view is visible
2. In the left sidebar, find your UAV (e.g., uav-01)
3. Click the **ARM** button to arm the UAV (motors will spin but not produce lift)
4. Click the **TAKEOFF** button to initiate takeoff to default altitude (5m)
5. Observe the UAV rise and stabilize at the target altitude
6. To land, click the **LAND** button
7. After landing, click **DISARM** to stop the motors

### 7.2 Multi-UAV Formation Flying
1. Arm all UAVs using the **ARM ALL** button in the swarm control panel
2. Takeoff all UAVs using the **TAKEOFF ALL** button
3. Wait for all UAVs to reach hover altitude
4. In the formation selector (bottom panel), choose a formation (e.g., V-Formation, Line, Grid)
5. Click **APPLY** to command the swarm to form the selected pattern
6. Observe as UAVs autonomously navigate to their formation positions
7. To change formations, select a different pattern and click **APPLY** again
8. To land the swarm, use the **LAND ALL** button

### 7.3 Waypoint Missions
1. Arm and takeoff your UAV(s) as described above
2. Open the mission planner (usually in the bottom panel)
3. Click on the 3D view to add waypoints (right-click to remove)
4. Adjust waypoint altitude by dragging the marker up/down
5. Set waypoint actions (hover, loiter, camera action, etc.) in the waypoint editor
6. Click **UPLOAD MISSION** to send the mission to the selected UAV
7. Click **START MISSION** to begin execution
8. Monitor progress in the mission status display

### 7.4 Fault Injection and Testing
1. While flying, open the **Wind & Fault Injector** panel (usually on the right)
2. **Wind Testing**:
   - Adjust wind speed and direction sliders
   - Observe how UAVs compensate for disturbances
   - Test different turbulence models
3. **Component Failures**:
   - Select individual UAVs from the dropdown
   - Click failure buttons (e.g., FAIL ENGINE, FAIL GPS, FAIL IMU)
   - Observe failsafe behaviors and swarm reconfiguration
4. **Battery Simulation**:
   - Adjust battery drain rate to test low-battery scenarios
   - Watch for automatic RTL (Return-to-Launch) triggers

## 8. Configuration

### 8.1 Backend Configuration
Backend configuration is located in the `server/config/` directory:

#### Key Configuration Files:
- `physics.yaml`: Physics engine parameters (gravity, air resistance, etc.)
- `estimator.yaml`: State estimator settings (complementary filter/EKF parameters)
- `controller.yaml`: Flight controller gains (position, attitude, rate controllers)
- `swarm.yaml`: Swarm coordination parameters (formation offsets, collision avoidance)
- `safety.yaml`: Safety system parameters (geofence, failsafe triggers)

#### Modifying Configuration:
1. Navigate to `server/config/`
2. Edit the desired YAML file using your preferred text editor
3. Restart the backend for changes to take effect
4. Most parameters have comments explaining their purpose and valid ranges

### 8.2 Frontend Configuration
Frontend configuration is managed through:
- `client/vite.config.ts`: Vite build settings and plugins
- `client/src/settingsStore.ts`: User-adjustable graphics and simulation settings
- `client/src/theme/`: CSS variables for UI customization

#### Common Frontend Settings:
- Graphics quality (in Settings → Graphics)
- UI theme (light/dark)
- Control sensitivity
- Telemetry history length
- Default map tileset

## 9. Troubleshooting

### 9.1 Common Issues and Solutions

#### Problem: Backend fails to start
**Symptoms**: Cargo build errors, missing dependencies, panics on startup
**Solutions**:
- Ensure Rust toolchain is up-to-date: `rustup update`
- Check that all dependencies are fetched: `cargo fetch`
- Verify you're in the correct directory (`pidron/`)
- Look at the error message for specific missing crates or version conflicts

#### Problem: Frontend fails to connect to backend
**Symptoms**: "Connection refused" or "WebSocket disconnected" messages in browser console
**Solutions**:
- Verify backend is running and listening on port 8080
- Check that both frontend and backend are running on the same machine/network
- Ensure no firewall is blocking the connection
- Try accessing `http://localhost:8080` directly to see if backend responds

#### Problem: Poor 3D performance / low FPS
**Symptoms**: Choppy animation, delayed UI response, high CPU/GPU usage
**Solutions**:
- Reduce graphics quality in Settings → Graphics
- Lower the number of simulated UAVs (modify `server/config/swarm.yaml`)
- Close other GPU-intensive applications
- Update graphics drivers
- Try running backend in release mode: `cargo run --release`

#### Problem: Simulation not behaving as expected
**Symptoms**: UAVs not responding to commands, strange physics behavior
**Solutions**:
- Check console output for error messages or warnings
- Verify that you've armed the UAVs before sending movement commands
- Ensure GPS lock is achieved (satellites > 6) for outdoor navigation modes
- Reset simulation by refreshing the browser page
- Check that time scale is set to 1.0x (not paused or slowed)

### 9.2 Getting Help
- **Documentation**: Refer to the full documentation in the `docs/` directory
- **Issues**: Search or file issues on the GitHub repository
- **Community**: Join the project Discord/Slack for real-time help
- **Logs**: Check both browser console (frontend) and terminal output (backend) for error messages

## 10. Next Steps

After completing this getting started guide, consider exploring:

### 10.1 Advanced Features
- **Offboard Mode**: Send custom setpoints via MAVLink or ROS2
- **Computer Vision Integration**: Connect to external vision pipelines
- **Gazebo Integration**: Use Pidron with Gazebo for more complex environments
- **Swarm Algorithms**: Implement and test custom swarm behaviors

### 10.2 Development and Customization
- **Backend Development**: See `docs/developer-guide/` for detailed API documentation
- **Frontend Development**: Modify UI components in `client/src/`
- **Adding New Sensors**: Extend the sensor simulation framework
- **Custom Physics Plugins**: Add novel propulsion or aerodynamic models

### 10.3 Research Applications
- **Control Algorithm Testing**: Implement and compare novel controllers
- **Swarm Intelligence**: Test consensus, flocking, or market-based algorithms
- **Fault Tolerance**: Study swarm behavior under various failure conditions
- **Human-Swarm Interaction**: Experiment with different control paradigms

### 10.4 Frequently Asked Questions

**Q: Can I simulate fixed-wing aircraft?**
A: Currently, Pidron focuses on multirotor UAVs. Fixed-wing support is planned for future releases.

**Q: How many UAVs can I simulate simultaneously?**
A: This depends on your hardware. On a modern desktop CPU, 50+ UAVs is typically achievable in real-time.

**Q: Can I use Pidron with ROS 2?**
A: Yes! Pidron provides a ROS 2 bridge package in the `ros2_bridge/` directory.

**Q: Is the simulation deterministic?**
A: Yes, when run with a fixed time step and no external randomness (like wind turbulence), the simulation is deterministic.

**Q: How do I record and replay flights?**
A: Use the Export/Import buttons in the UI to save/load flight data. For programmatic access, enable the mcap feature and use the ROS 2 bag interface.

---

*Happy flying! For more detailed information, refer to the Developer Guide (`docs/developer-guide/`) and Technical Reference (`docs/reference/`).* 
