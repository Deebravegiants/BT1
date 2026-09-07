# [M] October CMS XSS

## Summary
Severity: Medium
Advisory: GHSA-3p6c-9xhm-8x7h
CVE: CVE-2017-1000193
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3p6c-9xhm-8x7h
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=0 <1.0.413

## Details
October CMS build 412 is vulnerable to stored XSS in brand logo image name resulting in JavaScript code execution in the victim's browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000193
- https://github.com/octobercms/october
- https://github.com/octobercms/october/compare/v1.0.412...v1.0.413#diff-66d6dfe5e11488e1afefcb69b8bdaabfR31
