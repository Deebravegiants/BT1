# [C] free5GC's NEF nnef-oam route group is unauthenticated; no-token requests reach the OAM handler

## Summary
Severity: Critical
Advisory: GHSA-cmpj-2x3g-m7g3
CVE: CVE-2026-44327
CWE: CWE-306, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-cmpj-2x3g-m7g3
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nef` — affected >=0

## Details
### Summary
free5GC's NEF mounts the `nnef-oam` route group without inbound OAuth2/bearer-token authorization. A network attacker who can reach NEF on the SBI can hit the OAM route with no `Authorization` header at all and the handler returns `200 OK`. The current OAM handler is a stub that returns `null`, but the structural defect is route-group-scoped: the entire OAM route group has no inbound auth middleware, so every future OAM operation added to this group inherits the missing auth boundary by default. Same root cause as the NEF traffic-influence and PFD-management findings.

### Details
Validated against the NEF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/nef:v4.2.0`
- Runtime NEF commit: `5ce35eab`
- Docker validation date: 2026-03-11

NEF advertises `OAuth2 setting receive from NRF: true`, yet the OAM route group is mounted without any inbound auth middleware and answers unauthenticated `GET`s with `200 OK`.

Code evidence (paths in `free5gc/nef`):
- OAM route group mounted without auth middleware: `NFs/nef/internal/sbi/server.go:60`
- OAM route exposed at `/`: `NFs/nef/internal/sbi/api_oam.go:9`
- OAM processor returns `200 OK` directly: `NFs/nef/internal/sbi/processor/oam.go:9`
- NEF context only exposes outbound token acquisition (`GetTokenCtx`); there is no inbound authorization path: `NFs/nef/internal/context/nef_context.go:153`

### PoC
Reproduced against the running NEF at `http://10.100.200.19:8000` with no `Authorization` header:

```
curl -i http://10.100.200.19:8000/nnef-oam/v1/
```

Observed output:
```
HTTP/1.1 200 OK
null
```

NEF container logs (`docker logs nef`) show the request being served while OAuth is enabled:
```
[INFO][NEF][GIN] | 200 | GET | /nnef-oam/v1/
```

### Impact
Missing inbound authentication (CWE-306) and authorization (CWE-862) on the NEF OAM SBI route group. Severity is scored against the OAM route group's intended capability surface (Operations / Administration / Maintenance), NOT against the current stub handler. The current handler is a stub that returns `null`, but the defect is route-group-scoped: there is no auth middleware on the group at all, so every future OAM operation added behind this group inherits the missing inbound auth boundary by default.

Any party that can reach NEF on the SBI can:
- Probe and enumerate the OAM route surface anonymously today.
- Hit any future OAM-group endpoint (read, modify, restart-style operations) anonymously, because the auth boundary does not exist for this group.

Operators who assume `OAuth2 setting receive from NRF: true` enforces inbound auth on NEF are wrong for this route group.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/861
Upstream fix: https://github.com/free5gc/nef/pull/23

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-cmpj-2x3g-m7g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44327
- https://github.com/free5gc/free5gc/issues/861
- https://github.com/free5gc/nef/pull/23
- https://github.com/free5gc/free5gc
