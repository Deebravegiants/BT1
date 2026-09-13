# [H] nebula-mesh: Operator session tokens stored in plaintext in the database

## Summary
Severity: High
Advisory: GHSA-q4vm-pq3q-8wgq
CVE: CVE-2026-53603
CWE: CWE-312, CWE-522
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-q4vm-pq3q-8wgq
Type: github-advisory

## Affected
- Go: `github.com/forgekeep/nebula-mesh` — affected >=0 <0.3.8

## Details
## Impact

Operator session tokens are stored in plaintext in the `operator_sessions` table (the `token` column is the PRIMARY KEY). The session token is a 32-byte random hex value sent directly in a cookie and valid for 24 hours.

- `internal/models/operator.go:61` — `OperatorSession.Token` holds the plaintext token.
- `internal/store/sqlite_operators.go:590` — `CreateOperatorSession` inserts `sess.Token` verbatim.
- `internal/store/sqlite_operators.go:603,642,681,698` — lookups/updates/deletes use `WHERE token = ?` against the plaintext value.

Anyone who can read the database (backup, snapshot, file copy, or SQL-level disclosure) obtains every active session token and can hijack operator sessions directly, with no further authentication.

This is functionally identical to the plaintext enrollment-token issue fixed in GHSA-ghmh-jhmj-wcmf. API keys (`OperatorAPIKey.KeyHash`) and enrollment tokens (`EnrollmentToken.TokenHash`) already store only a SHA256 hash; session tokens were missed.

## Patches

Store only a SHA256 hash of the session token, mirroring API keys and enrollment tokens:
1. Add a `HashSessionToken` helper (alongside the existing token-hash helpers).
2. Migration to add a `token_hash` column.
3. Update `CreateOperatorSession`, `PromoteOperatorSession`, and `GetOperatorBySession` to write/look up by hash.
4. Drop the plaintext `token` column in a follow-up migration.

Sessions are ephemeral (24h TTL), so all active sessions can be invalidated on deployment — no backward compatibility needed.

## Workarounds

Restrict and encrypt database backups; rotate the operator database. These mitigate exposure but do not fix the underlying storage of plaintext tokens.

## Resources

- `internal/models/operator.go:58-66`
- `internal/store/sqlite_operators.go:577-698`
- Migration `005_operators.up.sql:27`
- Prior related advisory: GHSA-ghmh-jhmj-wcmf

## References
- https://github.com/forgekeep/nebula-mesh/security/advisories/GHSA-q4vm-pq3q-8wgq
- https://github.com/forgekeep/nebula-mesh/commit/7cb01bab281ded557f8b6c81dab5f48d4c10182e
- https://github.com/forgekeep/nebula-mesh
- https://github.com/forgekeep/nebula-mesh/releases/tag/v0.3.8
