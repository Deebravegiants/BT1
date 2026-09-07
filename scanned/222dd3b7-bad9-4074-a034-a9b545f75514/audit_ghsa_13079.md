# [M] Gila CMS Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rvjp-j5j4-c9j5
CVE: CVE-2020-20523
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-rvjp-j5j4-c9j5
Type: github-advisory

## Affected
- Packagist: `gilacms/gila` — affected >=0 <1.11.4

## Details
Cross Site Scripting (XSS) vulnerability in `adm_user` parameter in Gila CMS version 1.11.3, allows remote attackers to execute arbitrary code during the Gila CMS installation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-20523
- https://github.com/GilaCMS/gila/issues/41
- https://github.com/GilaCMS/gila
