# [M] SurrealDB: ES512 silently downgraded to ES384 due to jsonwebtoken crate limitation

## Summary
Severity: Medium
Advisory: GHSA-fwg2-gr34-q3w8
CWE: CWE-327
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-fwg2-gr34-q3w8
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
When a user configures `ALGORITHM ES512` for any JWT access method (`DEFINE ACCESS ... TYPE JWT ALGORITHM ES512`), SurrealDB silently substitutes ES384 at all four internal algorithm conversion points. This occurs because the underlying `jsonwebtoken` crate (v10.x) does not include an ES512 algorithm variant, so the mapping defaults to ES384 without raising an error, warning, or log message.
 
Users who provide the correct P-521 key type for ES512 will experience authentication handshake failures due to the curve mismatch with ES384 (which expects P-384).
 
### Impact
 
Authentication handshake failures when using ES512 with the correct P-521 key type, and when tokens are verified by external systems expecting real ES512 signatures. 
 
This vulnerability cannot be exploited to forge tokens or compromise the integrity or confidentiality of data handled by SurrealDB, as ES384 remains cryptographically strong.

### Patches
 
Versions prior to SurrealDB `v3.1.0` are vulnerable.
 
The patches for SurrealDB `v3.1.0` block new `DEFINE ACCESS` statements using `ALGORITHM ES512` with a clear error message and add deprecation warnings at runtime for existing stored ES512 definitions.

### Workarounds
 
Users should reconfigure affected JWT access methods to use a supported algorithm such as ES384 (with a P-384 key pair) or another supported algorithm. Review any `DEFINE ACCESS` statements specifying `ALGORITHM ES512` and update them accordingly.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-fwg2-gr34-q3w8
- https://github.com/surrealdb/surrealdb/pull/7226
- https://github.com/surrealdb/surrealdb/commit/bd043d73dad583219d7df2b91f81ab0054c53730
- https://github.com/surrealdb/surrealdb
