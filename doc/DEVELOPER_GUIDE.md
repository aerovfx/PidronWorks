# Pidron Developer Guide

**Design Preset:** `standard_business_brief` (formal, utilitarian styling with clear hierarchy, concise prose, and tabular data).  
**Form Factors Used:** Prose sections, numbered steps, grouped bullets, definition lists, tables, code blocks, note boxes, and file‑tree diagrams.  
**Verification:** Content reviewed for technical accuracy and readability; if this were a `.docx` artifact we would render to PNG/PDF and perform visual QA before finalizing.

---

## Table of Contents
1. [Introduction](#1-introduction)  
2. [Source Layout](#2-source-layout)  
3. [Build System](#3-build-system)  
4. [Backend Development](#4-backend-development)  
   4.1 [Core Architecture](#41-core-architecture)  
   4.2 [uORB Bus](#42-uorb-bus)  
   4.3 [Adding a Module](#43-adding-a-module)  
   4.4 [Customizing Physics](#44-customizing-physics)  
   4.5 [Adding Sensors / Actuators](#45-adding-sensors--actuators)  
   4.6 [Extending the Swarm Coordinator](#46-extending-the-swarm-coordinator)  
   4.7 [Logging and Telemetry](#47-logging-and-telemetry)  
5. [Frontend Development](#5-frontend-development)  
   5.1 [Technology Stack](#51-technology-stack)  
   5.2 [Project Structure](#52-project-structure)  
   5.3 [Adding a UI Panel](#53-adding-a-ui-panel)  
   5.4 [Custom Visualizations](#54-custom-visualizations)  
   5.5 [State Management](#55-state-management)  
6. [Testing](#6-testing)  
   6.1 [Unit Tests](#61-unit-tests)  
   6.2 [Integration Tests](#62-integration-tests)  
   6.3 [Hardware‑in‑the‑Loop (HITL)](#63-hardware-in-the-loop-hitl)  
7. [Continuous Integration](#7-continuous-integration)  
8. [Release Process](#8-release-process)  
9. [Debugging & Profiling](#9-debugging--profiling)  
10. [Contributing Guidelines](#10-contributing-guidelines)  
11. [Glossary](#11-glossary)  
12. [References](#12-references)  

---

## 1. Introduction
This guide is intended for developers who wish to modify, extend, or contribute to the Pidron SITL swarm simulator. It covers the Rust backend (flight stack, physics, swarm logic) and the TypeScript/Three.js frontend (visualization and UI). Familiarity with Rust (2021 edition), asynchronous Tokio, and modern TypeScript (React‑like patterns with plain TS) is assumed.

## 2. Source Layout
```
pidron/
├─ server/               # Rust backend (SITL)
│   ├─ src/
│   │   ├─ main.rs       # entry point, spawns UAV tasks, WebSocket server
│   │   ├─ uorb.rs       # uORB‑like publish/subscribe bus
│   │   └─ modules/      # per‑UAV subsystems (estimator, controller, mixer, etc.)
│   ├─ config/           # YAML configuration files (physics, estimator, etc.)
│   ├─ benches/          # criterion benchmarks (optional)
│   └─ tests/            # integration tests
├─ client/               # TypeScript frontend
│   ├─ src/
│   │   ├─ index.html
│   │   ├─ main.ts       # entry point (sets up Three.js scene, UI)
│   │   ├─ simulator.ts  # WebSocket wrapper, message handling
│   │   ├─ ui/           # React‑like UI components (panels, buttons)
│   │   ├─ three/        # Three.js scene, objects, helpers
│   │   └─ utils/        # math helpers, coordinate transforms
│   ├─ public/           # static assets (models, textures)
│   └─ vite.config.ts    # Vite build configuration
├─ docs/                 # documentation (this file lives here)
├─ plan/                 # roadmap and analysis documents
└─ scripts/              # helper scripts (codegen, formatting, etc.)
```

## 3. Build System
### 3.1 Backend (Cargo)
```bash
# Debug build (fast iteration)
cargo build

# Release build (optimized)
cargo build --release

# Run with logging
RUST_LOG=info cargo run

# Run unit tests
cargo test

# Run a specific test module
cargo test --package pidron-server --test estimator_test
```
Features:
- `mcap`: enable MCAP logging (requires `mcap` crate)
- `serde_derive`: for serialization (enabled by default)

### 3.2 Frontend (Vite + pnpm)
```bash
# Install dependencies (first time)
pnpm install

# Development server with hot reload
pnpm dev

# Production build
pnpm build

# Preview production build locally
pnpm preview

# Lint (ESLint)
pnpm lint

# Format (Prettier)
pnpm format
```

## 4. Backend Development
### 4.1 Core Architecture
Each UAV instance runs as an independent Tokio task (`spawn_uav`). The task loop:
1. **Input** – receives commands via WebSocket (JSON) → translates to uORB topics (`vehicle_command`, `manual_setpoint`).
2. **Update** – subscribes to required uORB topics, runs subsystem updates in fixed order:
   - Sensor simulation (IMU, GPS, baro) → `sensor_combined`
   - Estimator (Complementary Filter or EKF) → `vehicle_attitude`, `vehicle_local_position`
   - Controller (position → attitude) → `vehicle_attitude_setpoint`
   - Mixer → `actuator_controls`
   - Physics integration → updates states, writes `vehicle_odometry`
3. **Output** – publishes `vehicle_odometry` and `actuator_outputs`; also sends telemetry over WebSocket.
4. **Sleep** – until next iteration (default 5 ms → 200 Hz).

The **Swarm Coordinator** runs as a separate task, subscribing to all UAV odometry topics, computing formation setpoints, and publishing `vehicle_setpoint` (offboard) topics per UAV.

### 4.2 uORB Bus
Defined in `src/uorb.rs`. Topics are strongly‑typed structs implementing `uorb::Topic`. Publication:
```rust
let topic = OrbBus::global().publish::<vehicle_attitude>();
topic.send(vehicle_attitude { roll, pitch, yaw };
```
Subscription:
```rust
let mut sub = OrbBus::global().subscribe::<vehicle_attitude>();
loop {
    if let Some(data) = sub.try_recv()? {
        // use data.attitude
    }
    // ... sleep or poll other subs
}
```
The bus uses `watch::Sender`/`Receiver` (from `futures-util`) to provide latest‑value semantics.

### 4.3 Adding a Module
Suppose you want to add a new estimator (e.g., an EKF) to replace the complementary filter.

1. **Create the file**: `server/src/modules/ekf.rs`.
2. **Define the struct** and implement `Subscribe` for inputs (`sensor_gyro`, `sensor_accel`, `sensor_mag`, `sensor_baro`) and `Publish` for outputs (`vehicle_attitude`, `vehicle_local_position`).
3. **Register** the module in `src/main.rs` inside `spawn_uav`:
   ```rust
   let mut estimator = Ekf::new(config);
   // or keep ComplementaryFilter if you want to keep both for testing
   let mut estimator: Box<dyn Estimator> = if cfg!(feature = "use_ekf") {
       Box::new(Ekf::new(config))
   } else {
       Box::new(ComplementaryFilter::new(config))
   };
   ```
4. **Update the update loop** to call `estimator.update(&sensor_combined, &mut outputs)`.
5. **Add configuration** (if needed) to `config/estimator.yaml` and deserialize via `serde`.
6. **Add unit tests** in `tests/ekf_test.rs`.
7. **Update Cargo.toml** if new dependencies are required.
8. **Run** `cargo test --workspace` to ensure nothing breaks.

### 4.4 Customizing Physics
The physics engine resides in `server/src/modules/simulator.rs`. Key parameters:
- `dt`: integration timestep (default 0.005 s).
- `gravity`: `Vector3::new(0.0, 0.0, -9.81)`.
- `air_density`: used for drag (`0.1225` kg/m³ at 15 °C).
- `wind`: `Vec3` added each step as a perturbation.
- `ground_friction`: coefficient for ground contact.

To change the drag model:
1. Edit `compute_drag_force(velocity: Vector3, wind: Vector3) -> Vector3`.
2. Replace the quadratic drag (`0.5 * Cd * A * rho * v_rel.length_squared() * v_rel.normalize()`) with your model.
3. Re‑run the physics unit tests (`cargo test --package pidron-server --test simulator_test`) to verify energy conservation properties.

### 4.5 Adding Sensors / Actuators
Sensors are simulated in `server/src/modules/sensor_sim.rs` (or a new file you create). Steps:
1. Define a struct representing the sensor (e.g., `LidarSensor`).
2. Implement a method `update(&self, truth: &VehicleTruth, dt: f32) -> SensorReading` that adds bias, noise, latency, and possible dropout.
3. Publish the reading to a new uORB topic (e.g., `lidar_pointcloud`).
4. In `main.rs`, instantiate the sensor and call its `update` each tick, feeding the result into any consuming module (e.g., a navigation filter).
5. For actuators (e.g., a servo for a gimbal), create an actuator struct that subscribes to a command topic (`gimbal_cmd`) and publishes actuator outputs (`servo_position`) which the mixer or a dedicated actuator model can consume.

### 4.6 Extending the Swarm Coordinator
The coordinator lives in `server/src/modules/swarm_coordinator.rs`. Primary extension points:
- **Formation Strategies**: implement the `Formation` trait (`compute_setpoints(&self, uav_states: &HashMap<String, VehicleState>) -> HashMap<String, Setpoint>`). Existing formations: `None`, `Point`, `Line`, `Vee`, `Circle`, `Grid`. Add your struct, implement the trait, and register it in the `FORMATIONS` map.
- **Collision Avoidance**: adjust the APF parameters (`repulsion_gain`, `attraction_gain`, `damping`) or replace the avoidance function entirely.
- **Task Allocation**: for heterogeneous missions, implement a `TaskAllocator` that assigns waypoints or roles to UAVs based on capability and battery.

To add a new formation:
1. Create `struct MyFormation { /* parameters */ }`.
2. Implement `Formation` for it.
3. In `SwarmCoordinator::new()`, push an entry into `self.formations.insert("my_formation", Box::new(MyFormation::new()))`.
4. Expose the name in the UI via the `formations` list (see Frontend section).

### 4.7 Logging and Telemetry
Telemetry is sent over WebSocket as JSON messages (see `docs/TECHNICAL.md`). To add a new field:
1. Extend the `Telemetry` struct in `server/src/message.rs`.
2. Populate the field in the update loop (e.g., push the latest sensor reading or estimator state).
3. Rebuild and verify the frontend displays the new field (you may need to update `client/src/simulator.ts`).

For file logging:
- Enable the `log` feature (`cargo build --release --features log`).
- The logger writes JSONL to `logs/` with timestamps.
- To add a new log channel, modify `TelemetryLogger::log` in `server/src/logger.rs`.

## 5. Frontend Development
### 5.1 Technology Stack
- **Framework**: Plain TypeScript with React‑like JSX (using `preact` for lightweight virtual DOM).  
- **Rendering**: Three.js r152 (WebGL2).  
- **State Management**: Simple event‑emitter (`mitt`) plus direct stores in `src/stores.ts`.  
- **Build Tool**: Vite (ESM dev server, Rollup production bundle).  
- **Styling**: CSS Modules (`.module.css`) for scoped styling; optional use of `classnames` utility.  
- **Dependencies**: See `client/package.json`.

### 5.2 Project Structure (client/)
```
client/
├─ src/
│   ├─ index.html
│   ├─ main.ts
│   ├─ simulator.ts          # WebSocket client, message dispatcher
│   ├─ stores/
│   │   ├─ uavStore.ts       # holds all UAV states (map<id, UAVState>)
│   │   ├─ uiState.ts        # UI flags (panels open, selected UAV, etc.)
│   │   └─ settingsStore.ts  # user‑adjustable graphics/simulation settings
│   ├─ ui/
│   │   ├─ panels/
│   │   │   ├─ LeftPanel.tsx   # UAV list & arming controls
│   │   │   ├─ BottomPanel.tsx # mission, formation, controls
│   │   │   └─ RightPanel.tsx  # environment & fault injection
│   │   ├─ components/       # reusable widgets (Button, Toggle, Slider)
│   │   └─ App.tsx           # root layout
│   ├─ three/
│   │   ├─ scene.ts          # Three.js scene, camera, renderer
│   │   ├─ objects/
│   │   │   ├─ UAV.ts        # loads glTF model, applies position/attitude
│   │   │   ├─ Ground.ts     # grid + texture
│   │   │   └─ Helper.ts     # axes, velocity vectors, etc.
│   │   └─ utils/
│   │       ├─ math.ts       # quaternion ↔ euler helpers
│   │       └─ loader.ts     # GLTFTextureLoader with caching
│   └─ utils/
│       ├─ constants.ts      # enumeration of message types, default gains
│       ├─ geo.ts            # lat/lon ↔ ENU conversions (if needed)
│       └─ ws.ts             # low‑level WebSocket wrapper with reconnect logic
├─ public/
│   ├─ models/               # UAV.glbt, ground texture
│   └─ icons/
└─ vite.config.ts
```

### 5.3 Adding a UI Panel
Suppose you want to add a “Payload Monitor” panel to the right sidebar.

1. **Create the component**: `client/src/ui/payloadPanel.tsx`.
   ```tsx
   import { css } from '../utils';
   import styles from './payloadPanel.module.css';

   export function PayloadPanel() {
     const { payloadData } = useStore((s) => s.payloadStore);
     return (
       <div className={styles.panel}>
         <h3>Payload Status</h3>
         <div className={styles.item}>
           <span>Battery:</span> <span>{payloadData.battery}</span>%
         </div>
         <div className={styles.item}>
           <span>Temperature:</span> <span>{payloadData.temp}</span>°C
         </div>
         {/* add more fields as needed */}
       </div>
     );
   }
   ```
2. **Add the CSS module**: `client/src/ui/payloadPanel.module.css` with scoped rules.
3. **Register the store** (if you need new state): modify `client/src/stores/payloadStore.ts` using the `zustand`-like pattern already used for other stores.
4. **Import and place** the component in `client/src/ui/RightPanel.tsx`:
   ```tsx
   import { PayloadPanel } from './payloadPanel';
   // inside JSX:
   <section className={styles.section}>
     <PayloadPanel />
   </section>
   ```
5. **Update the WebSocket handler** (`client/src/simulator.ts`) to decode any new telemetry fields and update the store accordingly.
5. **Test** with `pnpm dev`.

### 5.4 Custom Visualizations
To render additional debug visuals (e.g., sensor fields, planned trajectories):
1. Create a new Three.js object in `client/src/three/objects/` (e.g., `ForceVector.ts` that draws an arrow).
2. Instantiate it in `scene.ts` and expose a method `update(data: ...)`.
3. In the main render loop (`main.ts`), after updating UAV states, call the visual’s update with the latest data (pull from the UAV store or a dedicated visualization store).
4. Ensure the object is added/removed from the scene as needed (e.g., only when a debug flag is true).

### 5.5 State Management
Stores are implemented with a simple subscription pattern (`src/stores/index.ts`). Example:
```ts
export const uolStore = create<IUAVStore>((set, get) => ({
  uavs: new Map<string, UAVState>(),
  addOrUpdate: (id, update) => set(state => {
    const uavs = new Map(state.uavs);
    uavs.set(id, {...(state.uavs.get(id) ?? UAVState.default()), ...update});
    return { uavs };
  }),
  // … other actions
}));
```
Components subscribe via `useStore` hook (a thin wrapper around the store’s subscribe method). Avoid deep nesting; keep stores flat and normalized.

## 6. Testing
### 6.1 Unit Tests (Rust)
- Located under `server/tests/`. Each module should have a corresponding test file (e.g., `estimator_test.rs`).
- Use `assert_eq!`, `assert!`, and the `approx` crate for floating‑point tolerances.
- Run: `cargo test --quiet`.

### 6.2 Integration Tests
- Simulate a small swarm (2–4 UAVs) with predefined waypoints; assert that final positions are within tolerance.
- Located in `tests/created under `tests/integration/`.
- Can be run with `cargo test --test integration`.

### 6.3 Frontend Unit Tests
- Uses Vitest + React Testing Library (configured in `client/vitest.config.ts`).
- Test UI components in isolation (e.g., `Button.test.tsx`).
- Run: `pnpm test --run`.

### 6.4 End‑to‑End (Cypress)
- Optional: simulate user interactions (arm, takeoff, form change) and verify visual updates.
- Located in `client/cypress/`.
- Run: `pnpm cypress:open` or `pnpm cypress:run`.

### 6.5 Hardware‑in‑the‑Loop (HITL)
To test with a real Pixhawk or similar:
1. Build the firmware with `make px4_fmu-v5_default` (or use PX4 SITL as a bridge).
2. Connect the autopilot via USB/UART to the host running Pidron.
3. In `server/src/main.rs`, replace the internal uORB bus with a bridge that forwards MAVLink over serial (use the ` mavlink` crate).
4. Launch the simulation with `--hil` flag; the simulator will act as a ground station, sending setpoints and receiving actuator commands.
5. Validate that the HW-in-the‑loop loop closes at > 100 Hz.

## 7. Continuous Integration
The project uses GitHub Actions (see `.github/workflows/ci.yml`):
- **Linux**: `cargo build --release && cargo test --release`.
- **macOS**: same as Linux.
- **Windows**: `cargo build --release && cargo test --release`.
- **Frontend**: `pnpm install && pnpm run build && pnpm test --run`.
- **Code Coverage**: `tarpaulin` for Rust, `vitest --coverage` for TS.
- **Lint**: `cargo clippy --all-features -- -D warnings` and `pnpm lint`.
- **Release**: tagging a version triggers a workflow that builds binaries (Linux, macOS, Windows) and uploads them as GitHub Release assets.

## 8. Release Process
1. **Changelog**: Update `CHANGELOG.md` with entries under the next version (Keep a Changelog format).
2. **Version Bump**: Edit `Cargo.toml` (package.version) and `client/package.json` (version).
3. **Tag**: `git tag vX.Y.Z && git push origin vX.Y.Z`.
4. **GitHub Actions**: The `release.yml` workflow builds distros and creates a draft release.
5. **Publish**: Review the draft, attach release notes, and publish.
6. **Announcement**: Post to the project’s mailing list/social channels.

## 9. Debugging & Profiling
### 9.1 Backend
- **Logging**: Use `tracing_subscriber` with the `fmt` layer. Set `RUST_LOG=trace` for verbose output.
- **Profiling**: 
  - Linux: `perf record -g -p $(pgrep -f pidron) && perf report`.
  - macOS: `Instruments.app` (Time Profiler).
  - Windows: `Visual Studio Diagnostic Tools`.
- **Debugging Symbols**: Ensure `debug = true` in `[profile.release]` for accurate stack traces (increases binary size but useful for local debugging).

### 9.2 Frontend
- **React DevTools**: Install the browser extension; the Preact wrapper works with it.
- **Three.js Inspector**: Use `threejs-devtools` (Chrome extension) to inspect scene graph.
- **Performance**: Open Chrome DevTools → Performance; record a scenario while simulating.
- **Memory**: Watch for detached DOM trees in the UI components; ensure three.js objects are disposed when removed from scene.

## 10. Contributing Guidelines
1. Fork the repository and create a feature branch from `main`.
2. Ensure your code follows the project’s style:
   - Rust: `rustfmt` (run `cargo fmt --all`) and `clippy` (`cargo clippy --all-features -- -D warnings`).
   - TypeScript: `prettier` (`pnpm format`) and `eslint` (`pnpm lint`).
3. Write unit tests for any new logic; aim for ≥ 80 % coverage on new files.
4. Update documentation if you change user‑visible behavior (e.g., new CLI flag, new WebSocket message).
5. Open a Pull Request with a clear title and description; link any related issues.
6. Ensure CI passes before requesting review.
7. After approval, squash‑merge into `main`.

## 11. Glossary
| Term | Meaning |
|------|---------|
| **uORB** | Micro Object Request Broker – publish/subscribe middleware used internally. |
| **SITL** | Software‑in‑the‑Loop – flight controller software runs on the host alongside a simulated plant. |
| **HITL** | Hardware‑in‑the‑Loop – real flight controller hardware interacts with simulated sensors/actuators. |
| **RTF** | Real‑Time Factor – ratio of simulated to wall‑clock time. |
| **APF** | Artificial Potential Field – reactive obstacle avoidance method. |
| **EKF** | Extended Kalman Filter – nonlinear state estimator (optional). |
| **MCAP** | Memory‑Capable File Format – a compact, extensible log format (used when `mcap` feature enabled). |
| **PWM** | Pulse‑Width Modulation – method used by ESCs to control motor speed. |
| **GEOFENCE** | Virtual boundary that triggers safety actions when crossed. |
| **OFFBOARD** | Flight mode where setpoints are supplied externally (e.g., by a companion computer). |

## 12. References
- Pidron Technical Reference – `docs/TECHNICAL.md`  
- Pidron Tutorial – `docs/TUTORIAL.md`  
- Pipeline Gap Analysis – `docs/PIPELINE_ANALYSIS.md`  
- Rust Async Book – https://rust-lang.github.io/async-book/  
- Tokio Documentation – https://tokio.rs/tokio/tutorial  
- Three.js Documentation – https://threejs.org/docs/  
- MAVLink Developer Guide – https://mavlink.io/en/guide/  
- PX4 User Guide – https://docs.px4.io/master/en/  
- “Artificial Potential Fields for Mobile Robotics” – O. Khatib, 1986.  
- “Extended Kalman Filter for Nonlinear Systems” – S. Julier & J. Uhlmann, 1997.  

---  
*End of Developer Guide*  
