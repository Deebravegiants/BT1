# [H] Oxia affected by server crash via race condition in session heartbeat handling

## Summary
Severity: High
Advisory: GHSA-5gqc-qhrj-9xw8
CVE: CVE-2026-40943
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-5gqc-qhrj-9xw8
Type: github-advisory

## Affected
- Go: `github.com/oxia-db/oxia` — affected >=0 <0.16.2

## Details
### Summary
A race condition between session heartbeat processing and session closure can cause the server to panic with `send on closed channel`. The `heartbeat()` method uses a blocking channel send while holding a mutex, and under specific timing with concurrent `close()` calls, this can lead to either a deadlock (channel buffer full) or a panic (send on closed channel after TOCTOU gap in `KeepAlive`).

### Impact
A remote client can trigger a server crash by sending rapid `KeepAlive` requests while a session is expiring or being closed. This is a denial-of-service vulnerability that crashes the entire data server process.

All versions are affected.

### Details
In `oxiad/dataserver/controller/lead/session.go`, the `heartbeat()` method performs a blocking `s.heartbeatCh <- true` send. If the channel buffer is full (size 1), this blocks while holding the session mutex, preventing `close()` from acquiring the lock to close the channel — a deadlock.

Additionally, in `session_manager.go`, `KeepAlive()` releases the session manager's read lock before calling `heartbeat()`, creating a TOCTOU window where the session can be removed and closed between the lookup and the heartbeat call.

### Patches
Fixed by changing `heartbeat()` to use a non-blocking `select` with a `default` case, and by holding the session manager read lock through the entire `KeepAlive()` operation.

### Workarounds
No workaround available.

## References
- https://github.com/oxia-db/oxia/security/advisories/GHSA-5gqc-qhrj-9xw8
- https://nvd.nist.gov/vuln/detail/CVE-2026-40943
- https://github.com/oxia-db/oxia
