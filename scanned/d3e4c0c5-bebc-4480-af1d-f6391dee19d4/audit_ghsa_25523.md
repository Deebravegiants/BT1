# [C] Unrestricted Upload of File with Dangerous Type in ButterCMS

## Summary
Severity: Critical
Advisory: GHSA-3v5x-qjrp-q2hq
CVE: CVE-2022-27260
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-3v5x-qjrp-q2hq
Type: github-advisory

## Affected
- npm: `buttercms` — affected >=0

## Details
An arbitrary file upload vulnerability in the file upload component of ButterCMS v1.2.8 allows attackers to execute arbitrary code via a crafted SVG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27260
- https://github.com/ButterCMS/buttercms-js
- https://www.youtube.com/watch?v=Tw8OhtVd-mE
