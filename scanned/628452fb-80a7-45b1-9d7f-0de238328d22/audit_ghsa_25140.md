# [M] Moodle Grade information disclosure in grade's external fetch functions

## Summary
Severity: Medium
Advisory: GHSA-mm73-86f9-5x5c
CVE: CVE-2021-20184
CWE: CWE-354
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mm73-86f9-5x5c
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.7
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.4
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.1

## Details
It was found in Moodle before version 3.10.1, 3.9.4 and 3.8.7 that a insufficient capability checks in some grade related web services meant students were able to view other students grades.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20184
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=417167
