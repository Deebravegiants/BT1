# [M] Parse Server has a session field immutability bypass via falsy-value guard

## Summary
Severity: Medium
Advisory: GHSA-f6j3-w9v3-cq22
CVE: CVE-2026-34574
CWE: CWE-697
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-f6j3-w9v3-cq22
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.7.0-alpha.14
- npm: `parse-server` — affected >=0 <8.6.69

## Details
### Impact

An authenticated user can bypass the immutability guard on session fields (`expiresAt`, `createdWith`) by sending a null value in a PUT request to the session update endpoint. This allows nullifying the session expiry, making the session valid indefinitely and bypassing configured session length policies.

### Patches

The truthiness-based guard checks were replaced with key-presence checks that reject any value for protected session fields, including null.

### Workarounds

There is no known workaround. A `beforeSave` trigger on `_Session` could be used to reject null values for `expiresAt` and `createdWith`.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-f6j3-w9v3-cq22
- https://nvd.nist.gov/vuln/detail/CVE-2026-34574
- https://github.com/parse-community/parse-server/pull/10347
- https://github.com/parse-community/parse-server/pull/10348
- https://github.com/parse-community/parse-server/commit/90802969fc713b7bc9733d7255c7519a6ed75d21
- https://github.com/parse-community/parse-server/commit/ebccd7fe2708007e62f705ee1c820a6766178777
- https://github.com/parse-community/parse-server
