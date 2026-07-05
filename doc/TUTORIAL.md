# Pidron — Quick Tutorial

This tutorial shows common workflows: quickstart, UI walkthrough and simple
scenarios to exercise the swarm features.

## Quickstart (local)

1. Install dependencies

```bash
# backend
cargo build --release

# frontend
pnpm install
# or npm install
```

2. Run backend and frontend

```bash
# Terminal 1: backend
cargo run --release

# Terminal 2: frontend (dev)
pnpm dev
# or npm run dev
```

3. Open Web UI: http://127.0.0.1:8080 (production) or the Vite URL shown in the
   dev terminal (e.g. http://localhost:5174).

## UI walkthrough

- Top bar: session status (SIM / FPS / runtime state).
- Left sidebar: UAV list and quick actions (select UAV, ARM, TAKEOFF, LAND).
- Main view: 3D scene with UAV meshes, trails and telemetry overlays.
- Bottom / right: mission controls, formation selector and wind / fault injectors.

## Simple scenarios

Scenario: simultaneous takeoff and V-formation

1. Click `ARM ALL` in the Swarm Control Panel.
2. Click `TAKEOFF ALL` — UAVs will climb to the default hover altitude.
3. Select `V-Formation` and `APPLY` — Swarm Coordinator will compute offsets
   and issue offboard setpoints.

Scenario: fault injection and recovery

1. While flying, open `Wind & Fault Injector`.
2. Increase `Wind Speed` to 6–8 m/s to observe drift and attitude corrections.
3. Select one UAV and click `FAIL ENGINE` — observe failover behavior and how
   neighbors avoid the falling vehicle.

## Developer tips

- Hot-reload frontend: modify `src/` files while `pnpm dev` is running.
- Add debug logging: backend uses `tracing`; set `RUST_LOG=debug` before running.

```bash
RUST_LOG=debug cargo run
```

- View raw telemetry: WebSocket messages follow the telemetry schema in
  `docs/TECHNICAL.md`.

## Recording & Replay

- By default sessions generate telemetry logs. Use the UI `Export` feature to
  save a session (JSON/rosbag-like) and `Import` to replay a scenario.

## Troubleshooting

- Port 8080 in use: stop other local servers or change the bind address in
  `server/main.rs`.
- `pnpm` missing: install via `npm i -g pnpm` or use `npm` commands instead.

## Next steps

- Build an AI policy: export the environment reward and observation schema and
  plug into your RL training loop (OpenAI Gym-style wrapper recommended).
- Integrate MAVLink: replace/customize the WS layer for MAVLink crate to
  interoperate with QGroundControl.
