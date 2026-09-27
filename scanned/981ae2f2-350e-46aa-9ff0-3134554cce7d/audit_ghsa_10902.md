# [M] Parse Server session creation endpoint allows overwriting server-generated session fields

## Summary
Severity: Medium
Advisory: GHSA-5v7g-9h8f-8pgg
CVE: CVE-2026-32742
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-5v7g-9h8f-8pgg
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.17
- npm: `parse-server` — affected >=0 <8.6.42

## Details
### Impact

An authenticated user can overwrite server-generated session fields (`sessionToken`, `expiresAt`, `createdWith`) when creating a session object via `POST /classes/_Session`. This allows bypassing the server's session expiration policy by setting an arbitrary far-future expiration date. It also allows setting a predictable session token value.

### Patches

The session creation endpoint now filters out server-generated fields from user-supplied data, preventing them from being overwritten.

### Workarounds

Add a `beforeSave` trigger on the `_Session` class to validate and reject or strip any user-supplied values for `sessionToken`, `expiresAt`, and `createdWith`.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-5v7g-9h8f-8pgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32742
- https://github.com/parse-community/parse-server/pull/10195
- https://github.com/parse-community/parse-server/pull/10196
- https://github.com/parse-community/parse-server
