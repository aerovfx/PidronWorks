# Pidron — Computer Vision and AI Integration Tutorial

This tutorial demonstrates how to integrate computer vision and AI/ML systems with Pidron for advanced perception capabilities. You'll learn how to:
- Connect external vision systems to Pidron's camera feed
- Process detections from the built-in computer vision module
- Implement custom object detection algorithms
- Use vision data for obstacle avoidance and target tracking

## Prerequisites

Before starting this tutorial, ensure you have:
- Completed the [Quickstart Tutorial](tutorial.md)
- Basic understanding of Rust and asynchronous programming
- Familiarity with computer vision concepts (bounding boxes, classification, etc.)
- Python 3.8+ installed (for the OpenCV example)

## Overview: Pidron's Computer Vision Architecture

Pidron includes a modular computer vision system designed for extensibility:

![Computer Vision Architecture](https://via.placeholder.com/800x400.png?text=CV+Architecture+Diagram)

### Key Components

1. **Camera Frame Publisher** (`modules/simulator.rs`): 
   - Generates simulated camera images from each UAV's perspective
   - Publishes `CameraFrame` messages via uORB at 30 FPS

2. **Computer Vision Module** (`modules/computer_vision.rs`):
   - Subscribes to camera frames
   - Processes images (currently generates mock detections)
   - Publishes `ObjectDetection` messages

3. **Object Detection Message** (`uorb.rs`):
   - Contains timestamp and array of `DetectedObject`
   - Each detection includes class ID, name, confidence, and bounding box

4. **Consumer Modules**:
   - Can subscribe to detection data for decision making
   - Examples: obstacle avoidance, target following, landing assistance

## Part 1: Understanding the Built-in Computer Vision Module

Let's examine how the existing computer vision module works:

```rust
// In modules/computer_vision.rs
pub async fn run(
    _bus: OrbBus,
    tx_detections: tokio::sync::watch::Sender<ObjectDetection>,
    rx_camera: tokio::sync::watch::Receiver<CameraFrame>,
) {
    // ... receives camera frames, generates mock detections, publishes them
}
```

This module currently creates random detections for demonstration purposes. In a real implementation, you would replace the mock detection generation with actual computer vision processing.

### Key Data Structures

```rust
// In uorb.rs
pub struct CameraFrame {
    pub timestamp: u64,
    pub width: u32,
    pub height: u32,
    pub format: String, // e.g., "RGB888", "YUV420"
    pub data: Vec<u8>,  // Raw image data
}

pub struct ObjectDetection {
    pub timestamp: u64,
    pub objects: Vec<DetectedObject>,
}

pub struct DetectedObject {
    pub class_id: u32,
    pub class_name: String,
    pub confidence: f32, // 0.0 to 1.0
    pub bbox: [f32; 4],  // [x, y, width, height] normalized to [0,1]
}
```

## Part 2: Connecting an External Vision System (Python/OpenCV Example)

In this section, we'll create an external Python process that:
1. Subscribes to Pidron's camera feed via WebSocket
2. Processes frames with OpenCV
3. Sends detection results back to Pidron

### Step 1: Modify Pidson to Accept External Detection Input

First, let's add a new uORB topic for external detections. (Note: In a real implementation, you would modify the source code. For this tutorial, we'll show what the changes would look like.)

```rust
// In uorb.rs - Add this to the message definitions
pub struct ExternalDetection {
    pub timestamp: u64,
    pub source: String, // Identifier for the vision system (e.g., "opencv_yolov8")
    pub objects: Vec<DetectedObject>,
}
```

### Step 2: Create the Vision Processing Pipeline

Let's create a Python script that connects to Pidron's WebSocket, processes video frames, and returns detections.

Create a new file `vision_bridge.py`:

```python
#!/usr/bin/env python3
"""
Computer Vision Bridge for Pidron
Connects to Pidron's WebSocket, processes camera frames with OpenCV,
and sends detection results back via custom WebSocket messages.
"""

import asyncio
import json
import cv2
import numpy as np
import websockets
import time
from typing import Dict, List

class PidronVisionBridge:
    def __init__(self, ws_url: str = "ws://localhost:8080/ws"):
        self.ws_url = ws_url
        self.websocket = None
        
    async def connect(self):
        """Connect to Pidron's WebSocket server"""
        self.websocket = await websockets.connect(self.ws_url)
        print(f"Connected to {self.ws_url}")
        
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            
    async def process_frame(self, frame_data: bytes, width: int, height: int) -> dict:
        """
        Process a camera frame and return detections
        This is where you would plug in your actual CV model
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(frame_data, np.uint8)
        # Assuming RGB format - adjust based on actual frame format
        img = nparr.reshape((height, width, 3))
        
        # Example: Simple color-based detection (replace with your ML model)
        detections = self.detect_objects_opencv(img)
        
        return {
            "timestamp": int(time.time() * 1000),
            "source": "opencv_color_detector",
            "objects": detections
        }
    
    def detect_objects_opencv(self, img: np.ndarray) -> List[dict]:
        """
        Example detection using color thresholding
        Replace this with your actual object detection model (YOLO, SSD, etc.)
        """
        detections = []
        
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        
        # Define range for red color (example - detect red objects)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 | mask2
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        h, w = img.shape[:2]
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Filter small detections
                x, y, w_box, h_box = cv2.boundingRect(contour)
                # Convert to normalized coordinates [0,1]
                bbox = [
                    x / w, 
                    y / h, 
                    w_box / w, 
                    h_box / h
                ]
                
                detections.append({
                    "class_id": 0,  # Custom class for "red_object"
                    "class_name": "red_object",
                    "confidence": 0.85,  # Fixed for demo - in reality based on detection quality
                    "bbox": bbox
                })
                
                # Limit to max 5 detections per frame for performance
                if len(detections) >= 5:
                    break
                    
        return detections
    
    async def run(self):
        """Main processing loop"""
        await self.connect()
        
        try:
            # We'll use a simple approach: listen for telemetry to get frame metadata
            # In reality, you might need to modify Pidron to send raw frames via a dedicated channel
            async for message in self.websocket:
                data = json.loads(message)
                
                if data.get("type") == "telemetry":
                    # Extract camera info (this would need to be added to telemetry)
                    # For now, we'll simulate receiving frames separately
                    pass
                    
                elif data.get("type") == "camera_frame":
                    # This message type would need to be added to Pidron
                    frame_data = bytes(data["data"])
                    width = data["width"]
                    height = data["height"]
                    
                    detections = await self.process_frame(frame_data, width, height)
                    
                    # Send detections back to Pidron
                    await self.websocket.send(json.dumps({
                        "type": "external_detections",
                        "data": detections
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection to Pidron lost")
        finally:
            await self.disconnect()

if __name__ == "__main__":
    bridge = PidronVisionBridge()
    asyncio.run(bridge.run())
```

### Step 3: Alternative Approach - Modify the Computer Vision Module Directly

Instead of an external bridge, you can directly modify Pidron's computer vision module to use a real ML model. Here's how you might modify `modules/computer_vision.rs` to use a TensorFlow model:

```rust
// Add to Cargo.toml
# tensorflow = "0.18.0"
# ort = "0.15.0"  # ONNX Runtime might be easier

use tch::{nn, Device, Tensor};
use std::path::Path;

struct YoloModel {
    model: nn::Module,
    // ... other model-specific fields
}

impl YoloModel {
    fn new<P: AsRef<Path>>(path: P) -> Result<Self, Box<dyn std::error::Error>> {
        // Load your trained model
        let mut vs = nn::VarStore::new(Device::Cpu);
        let model = nn::seq()
            .add(nn::conv2d(...))
            // ... define your model architecture
            .build(&vs.root());
        
        // Load weights
        vs.load(path)?;
        
        Ok(Self { model })
    }
    
    fn predict(&self, image: &Tensor) -> Tensor {
        self.model.forward_t(&image, false)
    }
}

// Modify the run function
pub async fn run(
    bus: OrbBus,
    tx_detections: tokio::sync::watch::Sender<ObjectDetection>,
    rx_camera: tokio::sync::watch::Receiver<CameraFrame>,
) -> Result<(), Box<dyn std::error::Error>> {
    // Initialize your model
    let model = YoloModel::new("path/to/your/model.pt")?;
    let mut rng = Lcg::new(42);
    let mut last_timestamp: u64 = 0;

    loop {
        // ... [same frame handling as before] ...
        
        // Process with real model instead of mock
        let detections = process_frame_with_model(&frame, &model)?;
        
        // Publish detections
        let _ = tx_detections.send(detections);
    }
}

fn process_frame_with_model(
    frame: &CameraFrame, 
    model: &YoloModel
) -> Result<ObjectDetection, Box<dyn std::error::Error>> {
    // 1. Preprocess image (resize, normalize, etc.)
    // 2. Run inference
    // 3. Postprocess results (NMS, confidence thresholding)
    // 4. Convert to DetectedObject format
    
    // Placeholder implementation
    Ok(ObjectDetection {
        timestamp: frame.timestamp,
        objects: vec![],
    })
}
```

## Part 3: Using Vision Data for Autonomous Behaviors

Once you have detection data flowing into Pidron, you can use it for various autonomous behaviors. Here are examples of how to consume detection data in your custom modules.

### Example: Obstacle Avoidance System

Create a new module that subscribes to detections and generates avoidance commands:

```rust
// modules/obstacle_avoidance.rs
use tokio::time::{sleep, Duration};
use crate::uorb::{OrbBus, ObjectDetection, ManualControlSetpoint};

pub async fn run(
    bus: OrbBus,
    rx_detections: tokio::sync::watch::Receiver<ObjectDetection>,
    tx_manual: tokio::sync::watch::Sender<ManualControlSetpoint>,
) {
    let mut last_timestamp: u64 = 0;
    
    loop {
        // Wait for new detection data
        let detections = rx_detections.borrow().clone();
        if detections.timestamp == last_timestamp {
            sleep(Duration::from_millis(20)).await;
            continue;
        }
        last_timestamp = detections.timestamp;
        
        // Process detections to avoid obstacles
        let mut avoidance = calculate_avoidance(&detections.objects);
        
        // Apply to manual control (this would be merged with pilot input)
        let mut current = tx_manual.borrow().clone();
        current.pitch += avoidance.pitch;
        current.roll += avoidance.roll;
        // ... apply other corrections
        
        let _ = tx_manual.send(current);
    }
}

fn calculate_avoidance(objects: &[DetectedObject]) -> ManualControlSetpoint {
    let mut avoidance = ManualControlSetpoint::default();
    
    for obj in objects {
        // Simple avoidance: move away from large, central objects
        let cx = obj.bbox[0] + obj.bbox[2] / 2.0; // center x
        let cy = obj.bbox[1] + obj.bbox[3] / 2.0; // center y
        let size = obj.bbox[2] * obj.bbox[3];     // normalized area
        
        if size > 0.1 && obj.confidence > 0.5 {  // Significant obstacle
            // Generate repulsive force
            let dx = cx - 0.5; // offset from center
            let dy = cy - 0.5;
            
            // Convert to control inputs (simplified)
            avoidance.roll -= dx * 0.5 * obj.confidence;
            avoidance.pitch -= dy * 0.5 * obj.confidence;
        }
    }
    
    avoidance
}
```

### Example: Target Following Behavior

```rust
// modules/target_follow.rs
pub async fn run(
    bus: OrbBus,
    rx_detections: tokio::sync::watch::Receiver<ObjectDetection>,
    tx_setpoint: tokio::sync::watch::Sender<PositionSetpoint>,
    target_class: String, // e.g., "person" or "landing_marker"
) {
    let mut last_timestamp: u64 = 0;
    
    loop {
        let detections = rx_detections.borrow().clone();
        if detections.timestamp == last_timestamp {
            sleep(Duration::from_millis(50)).await;
            continue;
        }
        last_timestamp = detections.timestamp;
        
        // Find target object
        if let Some(target) = detections.objects.iter()
            .find(|obj| obj.class_name == target_class && obj.confidence > 0.6) {
            
                // Calculate desired position to keep target centered
                let target_x = target.bbox[0] + target.bbox[2] / 2.0;
                let target_y = target.bbox[1] + target.bbox[3] / 2.0;
                
                // Error from center (0.5, 0.5)
                let error_x = target_x - 0.5;
                let error_y = target_y - 0.5;
                
                # // Simple proportional controller
                # let desired_vx = -error_y * 2.0;  # Negative because camera y-down vs world y-up
                # let desired_vy = -error_x * 2.0;
                #
                # # Convert velocity to position setpoint (simplified)
                # let mut current = tx_setpoint.borrow().clone();
                # current.velocity[0] += desired_vx * 0.1;
                #     current.velocity[1] += desired_vy * 0.1;
                #     let _ = tx_setpoint.send(current);
                # }
            }
        }
    }
```

## Part 4: Testing Your Vision Integration

Let's create a simple test to verify our computer vision pipeline works.

### Test 1: Validate the Mock Vision Module

First, let's verify the existing computer vision module is working by checking if it publishes detections:

```bash
# In one terminal
cargo run --release

# In another terminal, subscribe to debug topics or add logging
# You could modify the computer_vision.rs to print detections:
# println!("Published detections: {:?}", detections);
```

### Test 2: Test Your Custom Vision Bridge

If you implemented the Python bridge:

```bash
# Start Pidron
cargo run --release

# In another terminal, run your vision bridge
python3 vision_bridge.py

# You should see connection messages and periodic detection output
```

### Test 3: Verify Integration with Flight Stack

To test that detections actually affect flight behavior:

1. Enable your custom module in `main.rs` (add it to the autopilot_handles vector)
2. Look for objects in the simulation (the mock vision module generates random detections)
3. Observe if UAVs avoid or approach detected objects based on your logic

## Part 5: Advanced Topics

### 5.1 Optimizing for Real-time Performance

Computer vision processing can be computationally expensive. Consider these optimizations:

1. **Frame Skipping**: Process every Nth pixelated frame to reduce CPU/GPU load
2. **Resolution Reduction**: Process at lower resolution than the source feed
3. **Hardware Acceleration**: Use GPU via CUDA/TensorRT or specialized inference engines
4. **Async Pipeline**: Separate frame capture, processing, and result publishing into different tasks
5. **Model Optimization**: Use quantized models, pruning, or knowledge distillation

### 5.2 Handling Multiple Camera Feeds

For multi-UAV systems, each UAV may have its own camera:

```rust
// In your vision processing module
// Subscribe to camera streams for specific UAVs
let camera_subscribes: Vec<_> = (0..drone_count)
    .map(|i| {
        let rx = bus.subscribe::<CameraFrame>(); // Would need topic per UAV
        (format!("uav-{:02}", i+1), rx)
    })
    .collect();

// Process each stream separately
for (uav_id, mut rx) in camera_subscribes {
    tokio::spawn(process_uav_camera(uav_id, rx, tx_detections.clone()));
}
```

### 5.3 Data Fusion and Uncertainty Handling

Combine vision data with other sensor modalities:

```rust
// Example: Fuse vision with lidar and IMU
struct SensorFusion {
    vision_confidence: f32,
    lidar_confidence: f32,
    imu_confidence: f32,
    // ... Kalman filter or complementary filter state
}

fn fuse_sensor_data(
    vision_data: &[DetectedObject],
    lidar_points: &[Point3D],
    imu_data: &ImuReading
) -> RefinedObjectEstimate {
    # # Implement your fusion algorithm here
    # # Could be as simple as weighted average or as complex as particle filter
    # }
}
```

### 5.4 Safety Considerations

When integrating perception systems for flight control:

1. **Latency Budgets**: Ensure end-to-end delay < 100ms for reactive control
2. **Failure Modes**: Plan for sensor dropout, misdetection, and false positives
3. **Confidence Thresholding**: Only act on high-confidence detections
4. **Fallback Strategies**: Switch to safe behaviors when vision is unreliable
5. **Testing in Simulation**: Always validate in SITL before HITL or flight tests

## Part 6: Resources and Next Steps

### Recommended Learning Resources

1. **Computer Vision Fundamentals**:
   - "Computer Vision: Algorithms and Applications" by Richard Szeliski (free online)
   - OpenCV Documentation: https://docs.opencv.org/
   - Deep Learning for Computer Vision courses (CS231n, etc.)

2. **Pidron-Specific**:
   - [Technical Reference](../reference/technical.md) - System architecture
   - [WebSocket API Reference](../reference/websocket-api.md) - Message formats
   - [Developer Guide](../developer-guide/index.md) - Extending Pidron

### Project Ideas

1. **Landing Assistance System**: Use visual fiducials (AprilTags, ArUco markers) for precision landing
2. **Follow-Me Mode**: Track a colored vest or specific object using color histogram tracking
3. **Obstacle Avoidance**: Deploy stereo vision or depth sensing for 3D obstacle detection
4. **Swarm Perception**: Share detection data between UAVs for collective awareness
5. **Gesture Control**: Recognize hand gestures for intuitive UAV control

### Troubleshooting

| Symptom | Possible Cause | Solution |
|---------|----------------|----------|
| No detections appearing | Camera feed not connected | Verify camera topic publishing |
| High latency | Processing too slow | Reduce resolution, simplify model |
| False positives | Poor lighting/training | Adjust thresholds, improve training data |
| Control instability | Delayed vision feedback | Increase prediction horizon, add filtering |

## Conclusion

You've now learned how to integrate computer vision and AI systems with Pidron! Whether you're using the built-in mock vision module for prototyping or connecting to state-of-the-art deep learning models, Pidron's modular architecture makes it easy to experiment with advanced perception capabilities.

Remember to:
- Start simple with the existing computer vision module
- Gradually replace mock components with real implementations
- Always test thoroughly in simulation before attempting hardware integration
- Consider latency, reliability, and safety in your designs

Happy flying and coding! For more advanced topics, check out the [Developer Guide](../developer-guide/index.md) and explore the [reference documentation](../reference/).
