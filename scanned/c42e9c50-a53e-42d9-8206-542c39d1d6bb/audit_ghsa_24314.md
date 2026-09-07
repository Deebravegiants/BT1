# [H] Dolibarr Unrestricted Upload of File with Dangerous Type

## Summary
Severity: High
Advisory: GHSA-2gcp-xwxg-hqg3
CVE: CVE-2020-14209
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2gcp-xwxg-hqg3
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <11.0.5

## Details
Dolibarr before 11.0.5 allows low-privilege users to upload files of dangerous types, leading to arbitrary code execution. This occurs because .pht and .phar files can be uploaded. Also, a .htaccess file can be uploaded to reconfigure access control (e.g., to let .noexe files be executed as PHP code to defeat the .noexe protection mechanism).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14209
- https://github.com/Dolibarr/dolibarr
- https://github.com/Dolibarr/dolibarr/releases/tag/11.0.5
- https://www.wizlynxgroup.com/security-research-advisories/vuln/WLX-2020-012
- http://packetstormsecurity.com/files/161955/Dolibarr-ERP-CRM-11.0.4-Bypass-Code-Execution.html
