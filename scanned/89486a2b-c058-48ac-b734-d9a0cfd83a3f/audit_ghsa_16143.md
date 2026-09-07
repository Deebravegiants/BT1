# [M] moodle: IDOR in edit/delete RSS feed

## Summary
Severity: Medium
Advisory: GHSA-x3x9-349x-2485
CVE: CVE-2024-48897
CWE: CWE-285, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-x3x9-349x-2485
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.14
- Packagist: `moodle/moodle` — affected >=4.2.0 <4.2.11
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.8
- Packagist: `moodle/moodle` — affected >=4.4.0 <4.4.4

## Details
A vulnerability was found in Moodle. Additional checks are required to ensure users can only edit or delete RSS feeds that they have permission to modify.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48897
- https://bugzilla.redhat.com/show_bug.cgi?id=2318821
- https://github.com/moodle/moodle
