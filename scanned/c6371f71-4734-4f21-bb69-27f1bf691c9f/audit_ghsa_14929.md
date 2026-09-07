# [H] Dolibarr arbitrary file upload vulnerability

## Summary
Severity: High
Advisory: GHSA-p7r8-7w87-8g46
CVE: CVE-2024-37821
CWE: CWE-434, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-18
Source: https://github.com/advisories/GHSA-p7r8-7w87-8g46
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <19.0.2

## Details
An arbitrary file upload vulnerability in the Upload Template function of Dolibarr ERP CRM up to v19.0.1 allows attackers to execute arbitrary code via uploading a crafted .SQL file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37821
- https://github.com/Dolibarr/dolibarr
- https://github.com/alexbsec/CVEs/blob/master/2024/CVE-2024-37821.md
- http://dolibarr.com
