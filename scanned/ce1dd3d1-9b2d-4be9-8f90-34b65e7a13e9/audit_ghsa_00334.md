# [H] Prototype Pollution in defaults-deep

## Summary
Severity: High
Advisory: GHSA-cqp5-m4pq-gfgp
CVE: CVE-2018-3723
CWE: CWE-471
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-cqp5-m4pq-gfgp
Type: github-advisory

## Affected
- npm: `defaults-deep` — affected >=0 <0.2.4

## Details
Versions of `default-deep` before 0.2.4 are vulnerable to prototype pollution


## Recommendation

Update to version 0.2.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3723
- https://github.com/jonschlinkert/defaults-deep/commit/c873f341327ad885ff4d0f23b3d3bca31b0343e5
- https://hackerone.com/reports/310514
- https://github.com/advisories/GHSA-cqp5-m4pq-gfgp
- https://www.npmjs.com/advisories/581
