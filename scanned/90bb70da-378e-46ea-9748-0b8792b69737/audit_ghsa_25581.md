# [H] Access Control vulnerability in Dolibarr

## Summary
Severity: High
Advisory: GHSA-xw7v-qrhc-jjg2
CVE: CVE-2021-37517
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-01
Source: https://github.com/advisories/GHSA-xw7v-qrhc-jjg2
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <14.0.1

## Details
An Access Control vulnerability exists in Dolibarr ERP/CRM 13.0.2, fixed version is 14.0.1, in the forgot-password function becuase the application allows email addresses as usernames, which can cause a Denial of Service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37517
- https://github.com/Dolibarr/dolibarr/commit/b57eb8284e830e30eefb26e3c5ede076ea24037c
- https://github.com/Dolibarr/dolibarr
- https://github.com/Dolibarr/dolibarr/releases/tag/14.0.1
