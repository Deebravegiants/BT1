# [H] Dolibarr Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-r9cm-pw9j-3fpx
CVE: CVE-2023-4197
CWE: CWE-20, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-01
Source: https://github.com/advisories/GHSA-r9cm-pw9j-3fpx
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <18.0.2

## Details
Improper input validation in Dolibarr ERP CRM <= v18.0.1 fails to strip certain PHP code from user-supplied input when creating a Website, allowing an attacker to inject and evaluate arbitrary PHP code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4197
- https://github.com/Dolibarr/dolibarr/commit/0ed6a63fb06be88be5a4f8bcdee83185eee4087e
- https://github.com/Dolibarr/dolibarr
- https://starlabs.sg/advisories/23/23-4197
