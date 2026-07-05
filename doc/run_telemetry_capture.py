import time
import json
from websocket import create_connection, WebSocketTimeoutException

WS_CANDIDATES = [
    'ws://127.0.0.1:8080/api/ws',
    'ws://127.0.0.1:8080/ws',
    'ws://localhost:8080',
    'ws://localhost:8080/ws'
]
DURATION_SECONDS = 20
OUTPUT_FILE = 'docs/sample_telemetry.json'

def try_connect():
    for url in WS_CANDIDATES:
        try:
            print(f'Trying {url} ...')
            ws = create_connection(url, timeout=5)
            print('Connected to', url)
            return ws, url
        except Exception as e:
            print(f'Failed {url}: {e}')
    return None, None

if __name__ == '__main__':
    ws, used = try_connect()
    if not ws:
        print('Unable to connect to any WebSocket endpoint. Exiting.')
        raise SystemExit(1)
    start = time.time()
    collected = []
    print('Collecting for', DURATION_SECONDS, 'seconds...')
    while time.time() - start < DURATION_SECONDS:
        try:
            msg = ws.recv()
        except WebSocketTimeoutException:
            continue
        except Exception as e:
            print('Recv error:', e)
            break
        if not msg:
            continue
        try:
            obj = json.loads(msg)
        except Exception:
            continue
        if obj.get('type') == 'telemetry':
            collected.append({'t': time.time(), 'payload': obj})
    ws.close()
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(collected, f)
    print('Saved', len(collected), 'telemetry entries to', OUTPUT_FILE)
