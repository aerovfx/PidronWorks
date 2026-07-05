# Pidron Reference Documentation

This directory contains detailed reference documentation for Pidron.

## Available Documents

### [technical.md](technical.md)
Technical design document describing the high-level architecture, core modules, and data flow of the Pidron SITL swarm simulator.

### [pipeline-analysis.md](pipeline-analysis.md)
Analysis comparing Pidron's capabilities to a typical real-world drone stack, identifying implemented features and gaps.

### [configuration.md](configuration.md)
Reference for configuring Pidron through environment variables and runtime settings. Covers:
- Server port configuration
- Logging levels
- Default values and limitations

### [websocket-api.md](websocket-api.md)
Detailed reference of the WebSocket API used for client-server communication. Includes:
- Message formats for client-to-server commands
- Server-to-client telemetry structure
- Examples of common operations (arming, takeoff, wind control, etc.)

## Related Documentation

For getting started with Pidron, see:
- [`../getting-started/getting-started.md`](../getting-started/getting-started.md) - Installation and basic usage
- [`../user-guide/index.md`](../user-guide/index.md) - Complete user interface guide
- [`../tutorials/tutorial.md`](../tutorials/tutorial.md) - Quick tutorial with common scenarios

For development and contribution guidelines, see:
- [`../developer-guide/index.md`](../developer-guide/index.md) - Comprehensive developer guide
