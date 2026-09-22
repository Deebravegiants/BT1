# [M] Prototype pollution not blocked by object-path related utilities in hoolock

## Summary
Severity: Medium
Advisory: GHSA-4c2g-hx49-7h25
CVE: CVE-2024-23339
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-4c2g-hx49-7h25
Type: github-advisory

## Affected
- npm: `hoolock` — affected >=2.0.0 <2.2.1

## Details
### Impact
Utility functions related to object paths (`get`, `set` and `update`) did not block attempts to access or alter object prototypes.

### Patches
The `get`, `set` and `update` functions will throw a `TypeError` when a user attempts to access or alter inherited properties in versions >=2.2.1.

## References
- https://github.com/elijahharry/hoolock/security/advisories/GHSA-4c2g-hx49-7h25
- https://nvd.nist.gov/vuln/detail/CVE-2024-23339
- https://github.com/elijahharry/hoolock/commit/97ae80e856774335d92743c635ffeae2f652b982
- https://github.com/elijahharry/hoolock
