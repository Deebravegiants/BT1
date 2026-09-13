# [C] Prototype pollution in nestie

## Summary
Severity: Critical
Advisory: GHSA-m7rg-8wvq-846v
CVE: CVE-2021-25947
CWE: CWE-1321, CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-07
Source: https://github.com/advisories/GHSA-m7rg-8wvq-846v
Type: github-advisory

## Affected
- npm: `nestie` — affected >=0 <1.0.1

## Details
Prototype pollution vulnerability in 'nestie' versions 0.0.0 through 1.0.0 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25947
- https://github.com/lukeed/nestie/commit/bc80d5898d1e5e8a3d325d355eda0c325c8dcfc2
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25947
