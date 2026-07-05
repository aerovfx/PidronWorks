# Pidron WebSocket API Reference

This document describes the WebSocket API used for communication between the Pidron frontend and backend.

## Connection

The WebSocket server listens on `ws://localhost:8080/ws` by default. The port can be configured using the `PIDRON_PORT` environment variable.

```bash
PIDRON_PORT=8080 cargo run --release
```

## Message Format

All messages are JSON objects with a `type` field that determines the message structure.

### Client → Server Messages

#### Input Message
Send manual control inputs for the currently selected drone.

```json
{
  "type": "input",
  "pitch": -1.0 to 1.0,
  "roll": -1.0 to 1.0,
  "yaw": -1.0 to 1.0,
  "climb": -1.0 to 1.0,
  "mode": "string (optional, default: 'POSITION')",
  "source": "string (optional, default: 'idle')"
}
```

**Field Details:**
- `pitch`: Pitch angle (-1.0 = full forward, 1.0 = full backward)
- `roll`: Roll angle (-1.0 = full left, 1.0 = full right)
- `yaw`: Yaw rate (-1.0 = full left, 1.0 = full right)
- `climb`: Vertical speed (-1.0 = full down, 1.0 = full up)
- `mode`: Flight mode ("POSITION", "ALTITUDE", "MANUAL", etc.)
- `source`: Input source identifier ("idle", "joystick", "keyboard", etc.)

#### Command Message
Send commands to the currently selected drone.

```json
{
  "type": "command",
  "cmd": "string"
}
```

**Supported Commands:**
- `"arm"` - Arm the drone motors
- `"takeoff"` - Initiate takeoff sequence
- `"land"` - Initiate landing sequence
- `"emergency"` - Trigger emergency stop

**Note:** Command flags are automatically reset after 150ms.

#### Swarm Command Message
Send commands to all drones in the swarm.

```json
{
  "type": "swarm_command",
  "cmd": "string"
}
```

**Supported Commands:**
- `"arm_all"` - Arm all drone motors
- `"takeoff_all"` - Initiate takeoff for all drones
- `"land_all"` - Initiate landing for all drones
- `"emergency_all"` - Trigger emergency stop for all drones

#### Set Wind Message
Configure the global wind vector affecting all drones.

```json
{
  "type": "set_wind",
  "x": -10.0 to 10.0,
  "y": -10.0 to 10.0,
  "z": -10.0 to 10.0
}
```

**Field Details:**
- `x`: East-West wind component (m/s)
- `y`: Vertical wind component (m/s)
- `z`: North-South wind component (m/s)

#### Set Mission Message
Configure the current mission mode.

```json
{
  "type": "set_mission",
  "mode": "string"
}
```

**Supported Modes:**
- `"idle"` - No active mission
- `"takeoff"` - Execute takeoff sequence
- `"land"` - Execute landing sequence
- `"mission"` - Execute uploaded waypoint mission
- `"rtl"` - Return to launch
- `"loiter"` - Hold current position
- `"follow_me"` - Follow a moving target

#### Set Route Message
Configure the swarm routing behavior.

```json
{
  "type": "set_route",
  "route": "object"
}
```

**Structure:** The `route` object follows the `SwarmRoute` definition in the Rust code. Refer to `uorb.rs` for the complete structure.

### Server → Client Messages

#### Telemetry Message
Periodic updates containing the state of all drones in the swarm.

```json
{
  "type": "telemetry",
  "drones": {
    "uav-01": {
      "telemetry": {
        "armed": boolean,
        "phase": "string",
        "mode": "string",
        "x": float,
        "y": float,
        "z": float,
        "vx": float,
        "vy": float,
        "vz": float,
        "pitch": float (degrees),
        "roll": float (degrees),
        "heading": float (degrees, 0-360),
        "groundSpeed": float (m/s),
        "targetAltitude": float (meters),
        "battery": float (0-100),
        "signal": float (0-100),
        "satellites": integer,
        "warning": string or null
      },
      "motor_outputs": [float, float, float, float]  // 0.0 to 1.0 for each motor
    },
    "uav-02": { /* ... */ },
    // ... up to uav-08
  },
  "selected_id": "string",  // e.g., "uav-01"
  "input": {
    "pitch": float,
    "roll": float,
    "yaw": float,
    "climb": float,
    "source": string
  }
}
```

**Field Details:**
- `armed`: Whether the drone's motors are armed
- `phase`: Flight phase ("DISARMED", "GROUND", "TAKEOFF", "FLYING", "LANDING", etc.)
- `mode`: Current flight mode
- `x, y, z`: Position coordinates (meters)
- `vx, vy, vz`: Velocity components (m/s)
- `pitch, roll`: Attitude angles (degrees)
- `heading`: Compass heading (degrees, 0-360)
- `groundSpeed`: Horizontal speed magnitude (m/s)
- `targetAltitude`: Target altitude for position control (meters)
- `battery`: Battery charge percentage (0-100)
- `signal`: GPS signal quality (0-100)
- `satellites`: Number of GPS satellites in view
- `warning`: Warning message or null if none
- `motor_outputs`: Normalized motor commands (0.0 to 1.0) for each motor

## Message Rates

- Telemetry messages are sent at approximately 50Hz (every 20ms)
- Input messages should be sent at a maximum of 50Hz to avoid overwhelming the system
- Command messages are processed immediately but have built-in debouncing (150ms auto-reset)

## Error Handling

The WebSocket connection does not currently return explicit error messages for invalid commands. Clients should:
1. Validate input values before sending (-1.0 to 1.0 ranges for axes)
2. Observe the telemetry feedback to confirm command execution
3. Implement timeouts for expected state transitions

## Example Usage

### Arming a Drone
```javascript
// Select drone 1 (uav-01) first via UI or by sending a selection message
ws.send(JSON.stringify({
  "type": "command",
  "cmd": "arm"
}));
```

### Taking Off All Drones
```javascript
ws.send(JSON.stringify({
  "type": "swarm_command",
  "cmd": "takeoff_all"
}));
```

### Sending Manual Input
```javascript
ws.send(JSON.stringify({
  "type": "input",
  "pitch": 0.5,    // Pitch forward slightly
  "roll": 0.0,     // No roll
  "yaw": 0.2,      // Yaw right slightly
  "climb": 0.3,    // Climb gently
  "mode": "POSITION",
  "source": "keyboard"
}));
```

### Setting Wind Conditions
```javascript
ws.send(JSON.stringify({
  "type": "set_wind",
  "x": 5.0,   // 5 m/s from west
  "y": 0.0,   // No vertical wind
  "z": 0.0    // No north/south component
}));
```
