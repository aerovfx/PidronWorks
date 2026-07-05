# Pidron Configuration Reference

This document describes the configuration options available for Pidron.

## Environment Variables

Pidron can be configured using environment variables. These are read at startup and cannot be changed while the application is running.

### PIDRON_PORT
Specifies the port on which the WebSocket and HTTP servers will listen.

- **Format:** Integer (1-65535)
- **Default:** `8080`
- **Example:**
  ```bash
  PIDRON_PORT=3000 cargo run --release
  ```
  This will make the server available at `ws://localhost:3000/ws`

### RUST_LOG
Controls the logging level for the application. This is a standard environment variable used by the `tracing` crate.

- **Format:** `[module=]level[,module=level]*`
- **Default:** `info` (if not set)
- **Examples:**
  ```bash
  # Enable debug logging for all modules
  RUST_LOG=debug cargo run --release
  
  # Enable trace logging for networking components only
  RUST_LOG=tower_http=debug,cargo run --release
  
  # Enable info logging for the app, debug for websocket handling
  RUST_LOG=pixelron=info,tower_http=debug cargo run --release
  ```

**Available Modules:**
- `pilon` - Application-specific code
- `tower_http` - HTTP server functionality
- `tokio` - Async runtime
- `hyper` - HTTP implementation
- `tungstenite` - WebSocket implementation

## Configuration Files

Currently, Pidron does not support configuration files. All configuration must be done through environment variables as described above.

Future versions may support configuration files in YAML or TOML format for more complex settings such as:
- Drone physics parameters
- Controller gains
- Sensor noise characteristics
- Safety limits
- Swarm behavior parameters

## Runtime Configuration

While the core server configuration is fixed at startup, certain aspects of the simulation can be adjusted at runtime through the WebSocket API:

### Wind Settings
Adjust wind vectors using the `set_wind` WebSocket message:
```json
{
  "type": "set_wind",
  "x": 5.0,
  "y": 0.0,
  "z": 2.0
}
```

### Mission Settings
Change the current mission using the `set_mission` WebSocket message:
```json
{
  "type": "set_mission",
  "mode": "takeoff"
}
```

### Swarm Routing
Modify swarm behavior using the `set_route` WebSocket message:
```json
{
  "type": "set_route",
  "route": {
    // SwarmRoute structure as defined in uorb.rs
  }
}
```

## Hardware Limitations

When running Pidron, be aware of the following system resource constraints:

### Memory Usage
- Base memory: ~200MB
- Per drone: ~5-10MB
- Recommended minimum: 4GB RAM for smooth operation with 10+ drones

### CPU Usage
- Physics simulation runs at 200Hz
- Each drone requires approximately 2-5% of a modern CPU core
- A typical quad-core CPU can handle 20-30 drones in real-time

### GPU Requirements
- Minimum: OpenGL 3.3 compatible graphics card
- Recommended: Dedicated GPU with 2GB+ VRAM for smooth 3D rendering
- Headless mode available for server-only deployments

## Performance Tuning

For optimal performance with larger swarms, consider the following adjustments:

### Reduce Simulation Fidelity
Modify these constants in `server/modules/simulator.rs`:
- Decrease physics update frequency (currently 200Hz)
- Simplify drag and wind calculations
- Reduce sensor update frequency

### Optimize Rendering
Adjust these settings in the frontend:
- Lower graphics quality in Settings → Graphics
- Reduce the number of rendered particles/trails
- Disable post-processing effects
- Limit maximum frame rate

### Background Processes
When running benchmarks or headless simulations:
- Disable UI rendering entirely
- Run in release mode: `cargo run --release`
- Close unnecessary applications
- Consider using `taskset` or `numactl` for CPU affinity on Linux

## Security Considerations

### Network Exposure
By default, Pidron binds to localhost only (`127.0.0.1`). To make it accessible on other interfaces:

1. Change the IP address in `server/main.rs` line ~90:
   ```rust
   let address = SocketAddr::new(IpAddr::V4(Ipv4Addr::new(0, 0, 0, 0)), port);
   ```
   **WARNING:** This exposes the simulation to network access. Only do this on trusted networks.

2. Consider implementing authentication for WebSocket connections in production environments.

### Data Sensitivity
Pidron does not currently handle sensitive personal data. However, if you integrate with external systems (GPS data, video streams, etc.), consider:
- Encrypting sensitive data transmissions
- Implementing access controls
- Regularly updating dependencies to address security vulnerabilities

## Default Configuration Summary

When started with no environment variables, Pidron uses:
- WebSocket server: `ws://127.0.0.1:8080/ws`
- HTTP server: `http://127.0.0.1:8080` (serves frontend assets)
- Logging level: `info`
- Maximum drones: 8 (hardcoded in main.rs)
- Physics update rate: 200Hz
- Telemetry broadcast rate: ~50Hz
