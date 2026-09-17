# [C] Prototype Pollution in field

## Summary
Severity: Critical
Advisory: GHSA-hm82-qr45-h7mw
CVE: CVE-2020-28269
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-hm82-qr45-h7mw
Type: github-advisory

## Affected
- npm: `field` — affected >=0.0.1

## Details
Prototype pollution vulnerability in 'field' versions 0.0.1 through 1.0.1 allows attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28269
- https://github.com/jprichardson/field/blob/2a3811dfc4cdd13833977477d2533534fc61ce06/lib/field.js#L39
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28269
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28269,
