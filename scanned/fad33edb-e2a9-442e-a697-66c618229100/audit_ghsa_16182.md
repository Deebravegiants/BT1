# [M] moodle: IDOR when fetching report schedules

## Summary
Severity: Medium
Advisory: GHSA-mg54-p2wj-5ph7
CVE: CVE-2024-48901
CWE: CWE-285, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-mg54-p2wj-5ph7
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.14
- Packagist: `moodle/moodle` — affected >=4.2.0 <4.2.11
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.8
- Packagist: `moodle/moodle` — affected >=4.4.0 <4.4.4

## Details
A vulnerability was found in Moodle. Additional checks are required to ensure users can only access the schedule of a report if they have permission to edit that report.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48901
- https://bugzilla.redhat.com/show_bug.cgi?id=2318817
- https://github.com/moodle/moodle
