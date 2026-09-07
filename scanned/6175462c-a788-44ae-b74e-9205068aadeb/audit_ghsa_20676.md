# [M] Moodle reflected XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fcpw-vqh5-6qwj
CVE: CVE-2020-14320
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-17
Source: https://github.com/advisories/GHSA-fcpw-vqh5-6qwj
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.1
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.4
- Packagist: `moodle/moodle` — affected >=3.7 <3.7.7

## Details
In Moodle before 3.9.1, 3.8.4 and 3.7.7, the filter in the admin task log required extra sanitizing to prevent a reflected XSS risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14320
- https://github.com/moodle/moodle/commit/c6ffe9588ebb02b73c33a09e5d8061f58acc1701
- https://moodle.org/mod/forum/discuss.php?d=407392
