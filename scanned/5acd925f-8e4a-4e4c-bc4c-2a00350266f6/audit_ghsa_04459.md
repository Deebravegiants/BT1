# [C] nebula-mesh: API endpoints lack ownership checks, enabling cross-operator privilege escalation

## Summary
Severity: Critical
Advisory: GHSA-598g-h2vc-h5vg
CVE: CVE-2026-47724
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-598g-h2vc-h5vg
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0 <0.3.4

## Details
The `/api/v1/*` route surface trusts the bearer token alone for authorisation on most endpoints. The codebase itself admits this at `internal/api/hosts.go:384`: *"API trusts the bearer token for authorisation; per-CA ownership is enforced only in the Web layer."*

The Web UI gates state-changing routes through `loadAccessibleCA` (`internal/web/cas.go`); CA-management endpoints in `internal/api/cas.go` ALSO have proper `canAccessCA` gates. **The gap is on the host, network, firewall, mobile-bundle, and most operator endpoints.** Combined with the per-operator CA model from ADR 0002, this gives any non-admin operator API key broad cross-tenant access — instant privilege escalation in the worst case.

## Affected
All released versions prior to v0.3.4.

## Exploit chain

### A) Mint admin API key from any operator key (instant privilege escalation)
`internal/api/operators.go:118` — `handleCreateOperatorAPIKey` does no admin check and no actor/target-operator ownership check. Any operator key can call it for any operator (including admins) and receive a fresh bearer.

```
curl -X POST -H "Authorization: Bearer <low-priv-key>" \
  https://server/api/v1/operators/<admin-id>/api-keys \
  -H 'Content-Type: application/json' -d '{"name":"oops"}'
# Returns: {"key":"<32-byte admin bearer>","entry":{...}}
```

Reuse the returned key for subsequent requests → full admin.

### B) Cross-operator host takeover via reenroll
`internal/api/hosts.go:321,330` → `mintEnrollmentTokenForHost`. Looks up host by URL param, mints a single-use enrollment token, returns it. No ownership check.

```
curl -X POST -H "Authorization: Bearer <low-priv-key>" \
  https://server/api/v1/hosts/<victim-host-id>/reenroll
# Returns: {"enrollment_token":"<uuid>",...}
```

Caller POSTs `/api/v1/enroll` with their own X25519 + Ed25519 keypairs. `enroll.go:175` overwrites `signing_pub_pem`; `SaveCertificateAndEnrollHost` overwrites the cert. Legitimate agent's next signed poll fails `bad_signature`. Attacker now owns the victim's Nebula identity.

### C) Cross-tenant CRUD on hosts, networks, firewall
The same gap applies across:
- `/api/v1/hosts*` — create, list, get, update, delete, block, unblock
- `/api/v1/networks*` — create, list, get
- `/api/v1/networks/{id}/firewall` — get, PUT
- `/api/v1/hosts/{id}/mobile-bundle` (already filed as public issue #119)

All trust bearer-auth alone. Any operator can read or mutate any other operator's resources.

## Affected operator-management handlers (in addition to A)
Beyond `handleCreateOperatorAPIKey` (covered by A), `internal/api/operators.go` is missing admin gates on:
- `handleListOperators` (line 66) — operator roster info disclosure
- `handleDisableOperator` (line 79) — DoS / sabotage
- `handleEnableOperator` (line 94) — re-enable disabled operators
- `handleRevokeOperatorAPIKey` (line 157) — invalidate any operator's API keys
- `handleListOperatorAPIKeys` (line 173) — API-key metadata disclosure

`handleCreateOperator` (line 26) IS properly gated (`actorIsAdmin` at line 27).

## NOT affected (verified)
`internal/api/cas.go` properly gates every CA endpoint via `canAccessCA` (calls at lines 70, 176, 216) and admin shortcuts at lines 39, 82. An earlier description draft mistakenly listed `/api/v1/cas/{id}/rotate` as affected — that endpoint is properly protected. CAs are not in this gap.

## Impact
- Any non-admin operator → admin via one curl (A).
- Any non-admin operator → ownership of any victim's hosts with cert + identity transfer (B).
- Mass cross-tenant CRUD including firewall-rule mutation (C).
- Any operator → disable/enable other operators, revoke their API keys, enumerate the operator roster.

CVSS 3.1: AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H — 9.6.

## Suggested fix
Shared helpers in a new `internal/api/authz.go`, mirroring the Web layer's `loadAccessibleCA`:

```go
func (s *Server) requireAdmin(w http.ResponseWriter, r *http.Request) bool
func (s *Server) requireOperatorAccess(w http.ResponseWriter, r *http.Request, operatorID string) bool
func (s *Server) requireHostAccess(w http.ResponseWriter, r *http.Request, hostID string) (*models.Host, bool)
func (s *Server) requireNetworkAccess(w http.ResponseWriter, r *http.Request, networkID string) (*models.Network, bool)
```

Each loads the resource, resolves its CA via `*.CAID`, accepts if `actorIsAdmin(ctx)` OR actor owns the CA. Reject `403 forbidden`; audit-log `api.<resource>.forbidden` with the reason.

The operator-management endpoints take `requireAdmin` instead (operator ownership doesn't map to CA ownership).

Apply at the top of every host-, network-, firewall-, mobile-bundle-touching API handler, plus the 5 operator endpoints listed above. The legacy config-key path retains admin (preserves backward compatibility); the broader legacy-fallback question is tracked separately as issue #121.

## Test matrix
- admin → all operations permitted
- owning non-admin → operations on owned hosts/networks permitted
- non-owner non-admin → 403 + audit entry
- legacy config-key → preserved (admin)
- unauthenticated → existing 401 from middleware

## Coordinated context
Subsumes public issue #119 (mobile-bundle authz). Issue #121 (actor.go:40 legacy-admin fallback) is a separate concern tracked independently.

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-598g-h2vc-h5vg
- https://github.com/forgekeep/nebula-mesh/commit/9d8bcd7667ecd0c2975cc71fb35a02fe131f76f2
- https://github.com/juev/nebula-mesh
