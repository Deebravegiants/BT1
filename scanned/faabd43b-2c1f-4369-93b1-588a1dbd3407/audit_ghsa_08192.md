# [H] free5GC's SMF UPI POST /upi/v1/upNodesLinks exits the SMF process on overlapping UE pools (unauthenticated, reachable Fatalf)

## Summary
Severity: High
Advisory: GHSA-44qj-cghf-9p97
CVE: CVE-2026-44321
CWE: CWE-306, CWE-617, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-44qj-cghf-9p97
Type: github-advisory

## Affected
- Go: `github.com/free5gc/smf` — affected >=0

## Details
### Summary
free5GC's SMF mounts the `UPI` management route group without inbound OAuth2 middleware (same root cause as free5gc/free5gc#887). The `POST /upi/v1/upNodesLinks` create-or-update handler accepts attacker-controlled JSON and passes it directly into `UpNodesFromConfiguration()`, which calls `logger.InitLog.Fatalf(...)` on several validation failures. One confirmed path is the UE-IP-pool overlap check: a single unauthenticated POST that adds a new UPF whose pool overlaps an existing UPF terminates the entire SMF process (`docker ps` shows `Exited (1)`), not just the goroutine. This is a stronger sink than free5gc/free5gc#905: that one panics inside the request goroutine and Gin recovers; this one calls `Fatalf` which is `os.Exit(1)`-equivalent and kills the whole SMF process, dropping all of SMF's SBI surface (PDU-session establishment, UE policy lookups, etc.) until the process is restarted.

### Details
Validated against the SMF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/smf:v4.2.1`
- Runtime SMF commit: `8385c00a`
- Docker validation date: 2026-03-22 local (container log timestamp `2026-03-21T23:47:07Z`)
- SMF endpoint: `http://10.100.200.6:8000`

The broader `UPI` auth gap (#887) lets the unauthenticated POST reach the create/update handler. From there:

Vulnerable handler dispatches into topology parsing:
```
POST /upi/v1/upNodesLinks
 -> UpNodesFromConfiguration()
   -> isOverlap(allUEIPPools)
     -> logger.InitLog.Fatalf("overlap cidr value between UPFs")
```

Code evidence (paths in `free5gc/smf`):
- UPI group mounted WITHOUT auth middleware (preconditions for unauthenticated reachability):
  - `NFs/smf/internal/sbi/server.go:76`
  - `NFs/smf/internal/sbi/server.go:78`
- Create-or-update handler accepts attacker JSON and forwards it to `UpNodesFromConfiguration()`:
  - `NFs/smf/internal/sbi/api_upi.go:60`
  - `NFs/smf/internal/sbi/api_upi.go:72`
- Pool parsing (input from attacker JSON):
  - `NFs/smf/internal/context/user_plane_information.go:413`
- Overlap check that calls `Fatalf`:
  - `NFs/smf/internal/context/user_plane_information.go:479`

The same unauthenticated POST path also reaches sibling `Fatalf` calls for invalid-pool and static-pool-exclusion failures, so this is not a one-off code smell -- it is a class of attacker-reachable `Fatalf` call sites on a single unauthenticated handler:
- `NFs/smf/internal/context/user_plane_information.go:416`
- `NFs/smf/internal/context/user_plane_information.go:424`
- `NFs/smf/internal/context/user_plane_information.go:430`

### PoC
Reproduced end-to-end against the running SMF at `http://10.100.200.6:8000`.

1. Trigger: unauthenticated POST that adds a UPF with a UE pool overlapping the default UPF (`10.60.0.0/16`):
```
curl -i -X POST http://10.100.200.6:8000/upi/v1/upNodesLinks \
  -H 'Content-Type: application/json' \
  --data '{"links":[{"A":"gNB1","B":"UPF-OVERLAP-20260322"}],"upNodes":{"UPF-OVERLAP-20260322":{"type":"UPF","nodeID":"198.51.100.20","addr":"198.51.100.20","sNssaiUpfInfos":[{"sNssai":{"sst":1,"sd":"010203"},"dnnUpfInfoList":[{"dnn":"internet","pools":[{"cidr":"10.60.0.0/16"}]}]}]}}}'
```

Client-side observation (server died mid-request, no HTTP response written):
```
curl: (52) Empty reply from server
```

2. Confirm the SMF container exited:
```
docker ps -a --filter name=smf --format '{{.Names}}\t{{.Status}}'
```
```
smf    Exited (1) 9 seconds ago
```

3. SMF container logs (`docker logs --tail 80 smf`) show the `FATA` line that terminated the process:
```
[FATA][SMF][Init] overlap cidr value between UPFs
```

### Impact
Unauthenticated process-kill DoS on the SMF management plane.

1. Missing inbound authentication (CWE-306) and authorization (CWE-862) on the `UPI` route group makes the trigger reachable to any off-path network attacker who can reach SMF on the SBI -- no token, no UE state needed. The same-instance `nsmf-oam` returning `401` (see free5gc/free5gc#887) proves OAuth middleware is wired in for other SMF route groups and only missing on UPI.
2. Reachable assertion / fail-fast (CWE-617): topology parsing calls `logger.InitLog.Fatalf(...)` on attacker-influenced validation failures. `Fatalf` is `os.Exit(1)`-equivalent -- it skips Gin's recovery, the deferred handlers, and kills the whole SMF process. This is materially worse than the related panic-DoS in free5gc/free5gc#905, which Gin recovers from at the goroutine level.

Any party that can reach SMF on the SBI can:
- Send one unauthenticated POST with an overlapping UE pool and immediately terminate the SMF process, dropping all of SMF's SBI surface (PDU-session establishment, UE policy interactions) until SMF is restarted.
- Repeat the trigger after every restart to sustain the outage.
- Use sibling `Fatalf` paths (invalid-pool, static-pool exclusion) to sustain the same DoS even if the overlap check is hardened in isolation, because the underlying defect is using `Fatalf` for request-time validation on an unauthenticated handler.

No Confidentiality impact (the crash returns no data to the attacker). No persistent Integrity impact (the topology updates are in-memory and are lost when SMF dies). The whole impact concentrates in Availability: complete loss of SMF service via a single unauthenticated request.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/906
Upstream fix: https://github.com/free5gc/smf/pull/203

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-44qj-cghf-9p97
- https://nvd.nist.gov/vuln/detail/CVE-2026-44321
- https://github.com/free5gc/free5gc/issues/906
- https://github.com/free5gc/smf/pull/203
- https://github.com/free5gc/smf/commit/e0974e07ddab44a67d36a563cca383b2449e33e5
- https://github.com/free5gc/free5gc
