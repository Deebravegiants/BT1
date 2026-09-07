# [H] Microweber file upload vulnerability

## Summary
Severity: High
Advisory: GHSA-2c7x-w3mx-h7p6
CVE: CVE-2023-49052
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-30
Source: https://github.com/advisories/GHSA-2c7x-w3mx-h7p6
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0

## Details
File Upload vulnerability in Microweber v.2.0.4 allows a remote attacker to execute arbitrary code via a crafted script to the file upload function in the created forms component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49052
- https://github.com/Cyber-Wo0dy/CVE-2023-49052
- https://github.com/Cyber-Wo0dy/report/blob/main/microweber/v2.0.4/microweber_unrestricted_upload
- https://github.com/microweber/microweber
