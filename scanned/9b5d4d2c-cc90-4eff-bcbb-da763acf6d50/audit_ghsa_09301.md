# [H] @ranfdev/deepobj has a Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-x7q7-fchv-8h2j
CVE: CVE-2026-46509
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-x7q7-fchv-8h2j
Type: github-advisory

## Affected
- npm: `@ranfdev/deepobj` — affected >=0 <1.0.3

## Details
### Impact
Prototype pollution is possible when property paths contain `__proto__`/`constructor`/`prototype`. The property path must not be exposed as user input.

## References
- https://github.com/ranfdev/deepobj/security/advisories/GHSA-x7q7-fchv-8h2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-46509
- https://github.com/ranfdev/deepobj
