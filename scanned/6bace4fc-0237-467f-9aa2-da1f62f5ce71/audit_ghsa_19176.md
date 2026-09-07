# [H] Moodle has a stored XSS risk in admin live log

## Summary
Severity: High
Advisory: GHSA-wr88-x8cm-7cgq
CVE: CVE-2025-26529
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-24
Source: https://github.com/advisories/GHSA-wr88-x8cm-7cgq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.2
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.6
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.10
- Packagist: `moodle/moodle` — affected >=0 <4.1.16

## Details
Description information displayed in the site administration live log required additional sanitizing to prevent a stored XSS risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-26529
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=466145
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-84145
