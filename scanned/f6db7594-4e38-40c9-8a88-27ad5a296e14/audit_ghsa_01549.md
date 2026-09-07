# [H] dot-prop Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-ff7x-qrg7-qggm
CVE: CVE-2020-8116
CWE: CWE-1321, CWE-425, CWE-471
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-ff7x-qrg7-qggm
Type: github-advisory

## Affected
- npm: `dot-prop` — affected >=0 <4.2.1
- npm: `dot-prop` — affected >=5.0.0 <5.1.1

## Details
Prototype pollution vulnerability in dot-prop npm package versions before 4.2.1 and versions 5.x before 5.1.1 allows an attacker to add arbitrary properties to JavaScript language constructs such as objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8116
- https://github.com/sindresorhus/dot-prop/issues/63
- https://github.com/sindresorhus/dot-prop/commit/3039c8c07f6fdaa8b595ec869ae0895686a7a0f2
- https://github.com/sindresorhus/dot-prop/commit/c914124f418f55edea27928e89c94d931babe587
- https://hackerone.com/reports/719856
- https://github.com/advisories/GHSA-ff7x-qrg7-qggm
- https://github.com/sindresorhus/dot-prop
- https://github.com/sindresorhus/dot-prop/tree/v4
