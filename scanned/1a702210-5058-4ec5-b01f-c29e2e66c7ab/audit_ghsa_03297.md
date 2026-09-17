# [C] TypeORM vulnerable to MAID and Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-pf2j-9qmp-jqr2
CVE: CVE-2020-8158
CWE: CWE-1321, CWE-471
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-pf2j-9qmp-jqr2
Type: github-advisory

## Affected
- npm: `typeorm` — affected >=0 <0.2.25

## Details
Prototype pollution vulnerability in the TypeORM package < 0.2.25 may allow attackers to add or modify Object properties leading to further denial of service or SQL injection attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8158
- https://hackerone.com/reports/869574
