# [M] Moodle XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2hw6-6rgf-726v
CVE: CVE-2015-5337
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2hw6-6rgf-726v
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.11
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.9
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.3

## Details
Moodle through 2.6.11, 2.7.x before 2.7.11, 2.8.x before 2.8.9, and 2.9.x before 2.9.3 does not properly restrict the availability of Flowplayer, which allows remote attackers to conduct cross-site scripting (XSS) attacks via a crafted .swf file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5337
- https://github.com/moodle/moodle/commit/c73f6d03e5037729097bb9f5f5a55be15f3cab18
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=323232
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-48085
