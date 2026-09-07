# [M] Moodle reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-78fm-qhh8-8858
CVE: CVE-2021-32478
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-78fm-qhh8-8858
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.4
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.7
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.9

## Details
The redirect URI in the LTI authorization endpoint required extra sanitizing to prevent reflected XSS and open redirect risks. Moodle versions 3.10 to 3.10.3, 3.9 to 3.9.6, 3.8 to 3.8.8 and earlier unsupported versions are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32478
- https://github.com/moodle/moodle/commit/752ad3d8eb4f9ac22dbf1461aa69d6e0baee503e
- https://moodle.org/mod/forum/discuss.php?d=422314
