# [H] Prototype pollution in supermixer

## Summary
Severity: High
Advisory: GHSA-7prf-vw4p-qr59
CVE: CVE-2020-24939
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-7prf-vw4p-qr59
Type: github-advisory

## Affected
- npm: `supermixer` — affected >=0 <1.0.5

## Details
Prototype pollution in Stampit supermixer allows an attacker to modify the prototype of a base object which can vary in severity depending on the implementation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24939
- https://github.com/stampit-org/supermixer/issues/9
- https://github.com/stampit-org/supermixer/commit/94dcc6fc45e0fed96187cb52aaffadf76dbbc0a3
- https://hackerone.com/reports/959987
- https://github.com/stampit-org/supermixer/compare/v1.0.4...v1.0.5
