# [M] nebula-mesh's stores enrollment tokens unhashed in SQLite

## Summary
Severity: Medium
Advisory: GHSA-ghmh-jhmj-wcmf
CWE: CWE-312
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-ghmh-jhmj-wcmf
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0 <0.3.2

## Details
`internal/store/sqlite.go:1177,1192,1221,1245` — the `enrollment_tokens.token` column holds the raw UUID token. `ConsumeToken` does `WHERE token = ?` against the raw string. Compare with `operator_api_keys.key_hash`, which is SHA-256 hex (constructed in `internal/api/middleware.go:51-53`).

## Affected
All released versions up to v0.3.0.

## Threat model
Read access to `nebula-mgmt.db`: backup, snapshot, file-system access, future SQL-injection sink. The principle of defense-in-depth: API keys are hashed at rest; enrollment tokens — which grant the same lifecycle authority over a host's identity — are not.

An attacker who reads the DB before a legitimate agent enrolls can consume the single-use token first, mint a cert against their own keypair, and take the agent's intended Nebula identity.

## Suggested fix
1. Schema migration: rename `enrollment_tokens.token` → `token_hash` (or add the new column and drop the old after backfill of pending rows).
2. Store SHA-256 of token on create:
   ```go
   sum := sha256.Sum256([]byte(token))
   row.TokenHash = hex.EncodeToString(sum[:])
   ```
3. `ConsumeToken` accepts the raw token, hashes once, looks up by hash, atomically marks consumed.

Side bonus: take this opportunity to switch the token format from `uuid.New().String()` (122 bits) to `hex.EncodeToString(crypto/rand 32 bytes)` (256 bits), matching the project's session-token and API-key conventions. UUIDs are recognisable in logs and crash dumps; opaque hex blends in.

TOTP recovery codes appear to already be SHA-256 hashed at rest (`internal/web/totp.go:74-78`) — confirming that pattern is intentional elsewhere, just missed here.

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-ghmh-jhmj-wcmf
- https://github.com/juev/nebula-mesh
