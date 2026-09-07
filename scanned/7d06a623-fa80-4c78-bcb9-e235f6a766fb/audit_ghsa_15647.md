# [H] Dolibarr ERP CRM vulnerable to remote code execution (RCE) 

## Summary
Severity: High
Advisory: GHSA-vprp-94p9-5jp8
CVE: CVE-2024-40137
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-07-24
Source: https://github.com/advisories/GHSA-vprp-94p9-5jp8
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <19.0.2

## Details
Dolibarr ERP CRM before 19.0.2 was discovered to contain a remote code execution (RCE) vulnerability via the Computed field parameter under the Users Module Setup function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40137
- https://github.com/Dolibarr/dolibarr
- https://github.com/c0d3x27/CVEs/tree/main/CVE-2024-40137
