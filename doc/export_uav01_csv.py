import json
import csv

INPUT = 'docs/sample_telemetry.json'
OUTPUT = 'docs/sample_uav01_positions.csv'

with open(INPUT, 'r') as f:
    records = json.load(f)

rows = []
for rec in records:
    t = rec.get('t')
    payload = rec.get('payload', {})
    drones = payload.get('drones', {})
    info = drones.get('uav-01') or drones.get('uav_01') or None
    if not info:
        continue
    telemetry = info.get('telemetry', {})
    x = telemetry.get('x') or telemetry.get('pos', [None, None, None])[0]
    y = telemetry.get('y') or telemetry.get('pos', [None, None, None])[1]
    z = telemetry.get('z') or telemetry.get('pos', [None, None, None])[2]
    battery = telemetry.get('battery')
    rows.append((t, x, y, z, battery))

with open(OUTPUT, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['t', 'x', 'y', 'z', 'battery'])
    writer.writerows(rows)

print('Wrote', len(rows), 'rows to', OUTPUT)
