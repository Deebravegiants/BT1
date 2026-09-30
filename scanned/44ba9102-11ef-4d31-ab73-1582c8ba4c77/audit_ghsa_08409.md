# [H] free5GC's NEF nnef-callback route group is unauthenticated; forged callback requests are accepted into the processing path

## Summary
Severity: High
Advisory: GHSA-wqfh-gq79-j8mf
CVE: CVE-2026-44320
CWE: CWE-306, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-wqfh-gq79-j8mf
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nef` — affected >=0

## Details
### Summary
free5GC's NEF mounts the `nnef-callback` route group without inbound OAuth2/bearer-token authorization. A forged or arbitrary bearer token (e.g. `Authorization: Bearer not-a-real-token`) is enough to reach the SMF-callback handler -- the callback body is parsed and dispatched into NEF business logic instead of being rejected at the auth boundary. Same root cause as the other NEF SBI findings: the route group is mounted without any inbound auth middleware. NEF does not authenticate the producer NF identity before processing callback content; if an attacker can guess or obtain a valid `NotifId`, this missing auth boundary lets forged callbacks act on real subscription state. The route group is also reachable even when the runtime `ServiceList` does not declare it (it lists only `nnef-pfdmanagement` and `nnef-oam`).

### Details
Validated against the NEF container in the official Docker compose lab.
- Running Docker image: `free5gc/nef:v4.2.1`
- Docker validation date: 2026-03-11

NEF advertises `OAuth2 setting receive from NRF: true`, yet the `nnef-callback` route group is mounted with no inbound auth middleware. The API layer reads the raw request body and deserializes it before any auth check, then the processor looks up subscription state by `NotifId`.

Code evidence (paths in `free5gc/nef`):
- Callback route group mounted without auth middleware: `NFs/nef/internal/sbi/server.go:64`
- Callback route exposed at `/notification/smf`: `NFs/nef/internal/sbi/api_callback.go:13`
- API layer reads raw request bytes and deserializes them before any auth check: `NFs/nef/internal/sbi/api_callback.go:23`
- Processor looks up the subscription by `NotifId`: `NFs/nef/internal/sbi/processor/callback.go:13`
- NEF context only exposes outbound token acquisition (`GetTokenCtx`); there is no inbound authorization path: `NFs/nef/internal/context/nef_context.go:153`
- Config validation only allows `nnef-pfdmanagement` and `nnef-oam`: `NFs/nef/pkg/factory/config.go:126`

### PoC
Reproduced against the running NEF at `http://10.100.200.19:8000` using a fabricated bearer token.

Send a forged callback request:
```
curl -i \
  -H 'Authorization: Bearer not-a-real-token' \
  -H 'Content-Type: application/json' \
  --data '{"notifId":"forged-notif","eventNotifs":[]}' \
  http://10.100.200.19:8000/nnef-callback/v1/notification/smf
```

Observed output:
```
HTTP/1.1 404 Not Found
{"title":"Data not found","status":404,"detail":"Subscription is not found"}
```

The `404` is positive auth-bypass evidence: the request was parsed and dispatched into the callback business handler instead of being rejected at the auth boundary. NEF container logs (`docker logs nef`) confirm the callback handler was reached:
```
[INFO][NEF][TraffInfl] SmfNotification - NotifId[forged-notif]
[INFO][NEF][GIN] | 404 | POST | /nnef-callback/v1/notification/smf
```

### Impact
Missing inbound authentication (CWE-306) and authorization (CWE-862) on the NEF `nnef-callback` SBI route group. This is the trusted ingestion point for SMF -> NEF notifications. The defect is route-group-scoped: there is no auth middleware on the group at all, so every callback endpoint inside this group inherits the missing inbound auth boundary. Severity is scored against the route group's intended capability surface (consume SMF notifications and mutate NEF / downstream subscription state), NOT against the specific PoC where the chosen `NotifId` happened to be invalid.

Any party that can reach NEF on the SBI can:
- Submit forged SMF callbacks to NEF anonymously, with body content fully controlled by the attacker.
- Reach NEF callback business logic without proving producer NF identity, so any attacker who can guess or obtain a valid `NotifId` can deliver forged event notifications against real subscription state -- corrupting AF traffic-influence / PFD-management subscription views and the downstream SMF/UPF policy decisions that depend on them.
- Hit any future callback added behind this same route group anonymously, because the auth boundary does not exist for this group.

The `nnef-callback` route group is also reachable even when the runtime `ServiceList` does not declare it, so operators relying on `ServiceList` to disable the service do not actually get that protection.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/860
Upstream fix: https://github.com/free5gc/nef/pull/24

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-wqfh-gq79-j8mf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44320
- https://github.com/free5gc/free5gc/issues/860
- https://github.com/free5gc/nef/pull/24
- https://github.com/free5gc/free5gc
