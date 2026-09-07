# [M] Moodle sensitive information disclosure

## Summary
Severity: Medium
Advisory: GHSA-mmvj-j7hq-rx85
CVE: CVE-2015-5340
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mmvj-j7hq-rx85
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.11
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.9
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.3

## Details
Moodle through 2.6.11, 2.7.x before 2.7.11, 2.8.x before 2.8.9, and 2.9.x before 2.9.3 does not consider the moodle/badges:viewbadges capability, which allows remote authenticated users to obtain sensitive badge information via a request involving (1) `badges/overview.php` or (2) `badges/view.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5340
- https://github.com/moodle/moodle/commit/47d5c29202e299fdbe54229d3f6b0c381835eae3
- https://github.com/moodle/moodle/commit/65734f149f3c7e6cce9402f51f9a97deb31170db
- https://github.com/moodle/moodle/commit/7cff64fdbfff749e779cb625fbddcce737355100
- https://github.com/moodle/moodle/commit/d41fa94a69bebeca69a4cd5332bb9569cfd87b99
- https://github.com/moodle/moodle/commit/d70f610615242c5c7b3ae0bf7ef6868520dcd850
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=323235
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-51684
