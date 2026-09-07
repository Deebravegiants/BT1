# [M] Cross-Site Request Forgery in Moodle

## Summary
Severity: Medium
Advisory: GHSA-9328-7pcw-vw69
CVE: CVE-2020-1692
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-9328-7pcw-vw69
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <3.7.2

## Details
Moodle before version 3.7.2 is vulnerable to information exposure of service tokens for users enrolled in the same course.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1692
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1692
- https://github.com/moodle/moodle
