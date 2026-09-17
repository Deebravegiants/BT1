# [M] Prototype pollution in multi-ini

## Summary
Severity: Medium
Advisory: GHSA-67mq-h2r9-rh2m
CVE: CVE-2020-28460
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-67mq-h2r9-rh2m
Type: github-advisory

## Affected
- npm: `multi-ini` — affected >=0 <2.1.2

## Details
This affects the package multi-ini before 2.1.2. It is possible to pollute an object's prototype by specifying the constructor.proto object as part of an array. This is a bypass of CVE-2020-28448.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28460
- https://github.com/evangelion1204/multi-ini/commit/6b2212b2ce152c19538a2431415f72942c5a1bde
- https://snyk.io/vuln/SNYK-JS-MULTIINI-1053229
