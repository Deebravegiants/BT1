# [C] October CMS File Upload Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8vh6-8w76-v6m3
CVE: CVE-2017-1000194
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8vh6-8w76-v6m3
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=0 <1.0.413

## Details
October CMS build 412 is vulnerable to Apache configuration modification via file upload functionality resulting in site compromise and possibly other applications on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000194
- https://github.com/octobercms/october
- https://github.com/octobercms/october/compare/v1.0.412...v1.0.413#diff-c328b7b99eac0d17b3c71eb37038fd61R224
