# [M] Moodle allows users to retrieve information they did not have permission to access

## Summary
Severity: Medium
Advisory: GHSA-j822-x5gg-5r56
CVE: CVE-2024-45689
CWE: CWE-285, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-j822-x5gg-5r56
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.13
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.10
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.7
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.3

## Details
A flaw was found in Moodle. Dynamic tables did not enforce capability checks, which resulted in users having the ability to retrieve information they did not have permission to access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45689
- https://github.com/moodle/moodle/commit/bb466df202a4b4a692006298f93cbba20566949c
- https://bugzilla.redhat.com/show_bug.cgi?id=2309941
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=461894#p1854491
