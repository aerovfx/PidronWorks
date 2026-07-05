# Pidron Release Notes v0.1.0

**Release Date:** July 4, 2025  
**Version:** 0.1.0  
**Status:** Initial Release

## Overview

This is the initial release of Pidron, a Software-in-the-Loop (SITL) swarm simulator for multi-UAV research and development. Pidron provides a realistic physics-based environment, a modular autopilot stack, a swarm coordination layer, and a web-based 3D visualization interface.

## New Features

### Core Simulation
- **Rust-based Backend**: High-performance simulation engine built with Rust and Tokio for asynchronous operations
- **WebSocket Communication**: Real-time bidirectional communication between frontend and backend
- **Physics Engine**: 200Hz physics simulation with gravity, drag, wind perturbation, and ground contact modeling
- **uORB-like Message Bus**: Asynchronous publish/subscribe system for inter-module communication
- **Multi-UAV Support**: Capable of simulating multiple UAVs simultaneously (default: 8 vehicles)

### Flight Stack
- **Modular Architecture**: Separate modules for commander, estimator, position controller, attitude controller, mixer, and simulator
- **Sensor Simulation**: IMU, GPS, and barometer simulation with realistic noise characteristics
- **Estimator**: Complementary filter for attitude and position estimation
- **Control System**: Cascaded position-attitude controller architecture
- **Motor Mixing**: Configurable mixer for converting control signals to motor outputs

### Swarm Intelligence
- **Swarm Coordinator**: Central entity managing swarm-wide behaviors
- **Formation Control**: Support for various formations (V-formation, line, grid, etc.)
- **Collision Avoidance**: Artificial Potential Field (APF) based obstacle avoidance
- **Offboard Control**: Ability to send setpoints to individual UAVs for custom behaviors

### Safety Systems
- **Geofencing**: Virtual boundaries that trigger safety actions when crossed
- **Battery Monitoring**: Simulated battery drain with low-battery warnings
- **Failsafe Handling**: Automatic responses to critical failures
- **Emergency Stop**: Immediate motor cutoff capability

### Visualization & UI
- **3D Rendering**: Three.js-based visualization with realistic UAV models
- **Web Interface**: Reactive UI built with TypeScript and Preact
- **Real-time Telemetry**: Live updates of UAV status, position, and sensor data
- **Interactive Controls**: Arm/disarm, takeoff/land, formation selection, and manual controls
- **Environmental Controls**: Adjustable wind, gravity, and other environmental factors
- **Fault Injection**: Tools for simulating various failure scenarios (engine failure, GPS loss, etc.)

### Developer Experience
- **Hot Reloading**: Frontend development with Vite for instant updates
- **Comprehensive Logging**: Structured logging with adjustable verbosity via RUST_LOG
- **Clean Codebase**: Modular Rust code with clear separation of concerns
- **Cross-platform**: Supports Linux, macOS, and Windows

## Technical Details

### Backend
- **Language**: Rust 2021 edition
- **Framework**: Axum for HTTP/WebSocket server
- **Async Runtime**: Tokio
- **Dependencies**: 
  - `axum` (web framework)
  - `tokio` (async runtime)
  - `serde` (serialization)
  - `tracing` (logging)
  - `tower-http` (HTTP utilities)

### Frontend
- **Language**: TypeScript
- **Framework**: Preact (React-like library for lightweight UI)
- **Rendering**: Three.js r152 (WebGL2)
- **Build Tool**: Vite
- **State Management**: Custom event emitter with stores
- **Styling**: CSS Modules for scoped styling

### Communication Protocol
- **WebSocket**: Real-time bidirectional communication on `ws://localhost:8080/ws`
- **Message Format**: JSON-based protocol with typed messages
- **Message Types**:
  - `input`: Manual control commands (pitch, roll, yaw, climb)
  - `command`: Individual UAV commands (arm, takeoff, land, emergency)
  - `swarm_command`: Broadcast commands to all UAVs
  - `set_wind`: Configure global wind vector
  - `set_mission`: Set mission mode
  - `set_route`: Configure swarm routing behavior
  - `telemetry`: Server-to-client updates with full swarm state

## System Requirements

### Minimum
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10
- **CPU**: Modern x86_64 processor with at least 2 cores
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB available space
- **Graphics**: GPU with OpenGL 3.3+ support

### Software Dependencies
- **Rust**: 1.65+ (via rustup)
- **Node.js**: 16.x or 18.x
- **Package Manager**: pnpm (recommended) or npm/yarn
- **Git**: For version control

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/aerovfx/pidron.git
cd pidron
```

### 2. Install Rust Toolchain
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustup update stable
```

### 3. Install Node.js Dependencies
```bash
# Using nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 18
nvm use 18

# Install pnpm globally
npm install -g pnpm
```

### 4. Install Project Dependencies
```bash
# Backend dependencies
cargo fetch

# Frontend dependencies
pnpm install
# or: npm install
```

## Quick Start

### Development Mode
```bash
# Terminal 1: Start backend
cargo run

# Terminal 2: Start frontend (hot reload)
pnpm dev

# Open browser to: http://localhost:5174
```

### Production Mode
```bash
# Build backend
cargo build --release

# Install frontend dependencies (if not done)
pnpm install

# Start backend
cargo run --release

# Build frontend
pnpm build

# Preview production build locally
pnpm preview

# Open browser to: http://localhost:8080
```

## Known Limitations

1. **Fixed UAV Count**: Currently hardcoded to 8 UAVs in `server/main.rs`
2. **Limited Airframe Types**: Only multirotor UAVs supported in this release
3. **Basic Sensor Models**: Sensor noise models are simplified representations
4. **No MAVLink Support**: Uses custom JSON WebSocket protocol (planned for future)
5. **Limited Formation Types**: Basic formations implemented, advanced swarm algorithms pending
6. **Single Map**: Default terrain with helipad only, no terrain variation

## Backwards Compatibility

This is the initial release, so there are no previous versions to maintain compatibility with.

## Upgrading

As this is the first release, no upgrade instructions are needed.

## Contributing

We welcome contributions! Please see the [Developer Guide](../developer-guide/index.md) for:
- Setting up your development environment
- Code style guidelines
- Testing procedures
- How to submit pull requests

## Support

For issues, questions, or discussions:
- **GitHub Issues**: [https://github.com/aerovfx/pidron/issues](https://github.com/aerovfx/pidron/issues)
- **Documentation**: See the `docs/` directory for comprehensive guides
- **Examples**: Check the `tutorials/` and `user-guide/` directories for getting started

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Thanks to the open-source community for the excellent tools and libraries that made this project possible, particularly:
- The Rust ecosystem and Tokio team
- The Three.js authors for incredible WebGL capabilities
- The Preact team for lightweight UI solutions
- The Vite team for modern build tooling

---
*Generated on: July 4, 2025*
