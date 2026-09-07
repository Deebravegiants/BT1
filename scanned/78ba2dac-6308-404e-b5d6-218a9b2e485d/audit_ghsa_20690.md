# [H] Moodle Incorrect Authorization vulnerability

## Summary
Severity: High
Advisory: GHSA-9q29-jcjw-fw7h
CVE: CVE-2020-14321
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-17
Source: https://github.com/advisories/GHSA-9q29-jcjw-fw7h
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9.0-beta <3.9.1
- Packagist: `moodle/moodle` — affected >=3.8.0-beta <3.8.4
- Packagist: `moodle/moodle` — affected >=3.6.0-beta <3.7.7
- Packagist: `moodle/moodle` — affected >=0 <3.5.13

## Details
In Moodle before 3.9.1, 3.8.4, 3.7.7 and 3.5.13, teachers of a course were able to assign themselves the manager role within that course.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14321
- https://github.com/moodle/moodle/commit/d07fb8b9e8bf47fe60ad2aea553329bd1fb96e37
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=407393
