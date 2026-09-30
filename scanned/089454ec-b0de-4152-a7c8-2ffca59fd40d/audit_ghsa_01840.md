# [C] Prototype Pollution in putil-merge

## Summary
Severity: Critical
Advisory: GHSA-9x7m-9hpg-xxmw
CVE: CVE-2021-25953
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-9x7m-9hpg-xxmw
Type: github-advisory

## Affected
- npm: `putil-merge` — affected >=1.0.0 <3.7.0

## Details
Prototype pollution vulnerability in 'putil-merge' versions1.0.0 through 3.6.6 allows attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25953
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25953
