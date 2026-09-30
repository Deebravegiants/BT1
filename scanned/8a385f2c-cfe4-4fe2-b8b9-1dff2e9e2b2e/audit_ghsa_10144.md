# [M] Parse Server's Endpoint `/sessions/me` bypasses `_Session` `protectedFields`

## Summary
Severity: Medium
Advisory: GHSA-g4v2-qx3q-4p64
CVE: CVE-2026-39381
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-g4v2-qx3q-4p64
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.8.0-alpha.7
- npm: `parse-server` — affected >=7.0.0 <8.6.75

## Details
### Impact

The `GET /sessions/me` endpoint returns `_Session` fields that the server operator explicitly configured as protected via the `protectedFields` server option. Any authenticated user can retrieve their own session's protected fields with a single request. The equivalent `GET /sessions` and `GET /sessions/:objectId` endpoints correctly strip protected fields.

### Patches

The `GET /sessions/me` handler now re-fetches the session with the caller's auth context after validating the session token, ensuring `protectedFields` and CLP apply consistently with other session endpoints.

### Workarounds

None.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-g4v2-qx3q-4p64
- Fix Parse Server 9: https://github.com/parse-community/parse-server/pull/10406
- Fix Parse Server 8: https://github.com/parse-community/parse-server/pull/10407

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-g4v2-qx3q-4p64
- https://nvd.nist.gov/vuln/detail/CVE-2026-39381
- https://github.com/parse-community/parse-server/pull/10406
- https://github.com/parse-community/parse-server/pull/10407
- https://github.com/parse-community/parse-server
