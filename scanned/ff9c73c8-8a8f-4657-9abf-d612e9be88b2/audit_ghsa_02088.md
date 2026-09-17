# [C] Prototype pollution vulnerability in js-extend

## Summary
Severity: Critical
Advisory: GHSA-mh82-55cm-6gfh
CVE: CVE-2021-25945
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-mh82-55cm-6gfh
Type: github-advisory

## Affected
- npm: `js-extend` — affected >=0

## Details
Prototype pollution vulnerability in 'js-extend' versions 0.0.1 through 1.0.1 allows attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25945
- https://github.com/vmattos/js-extend
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25945
