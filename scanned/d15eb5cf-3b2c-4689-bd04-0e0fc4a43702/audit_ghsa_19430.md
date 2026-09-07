# [M] Moodle has an IDOR in web service which allows users enrolled in a course to access some details of other users

## Summary
Severity: Medium
Advisory: GHSA-6g5x-h5x7-q4mq
CVE: CVE-2025-3640
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-6g5x-h5x7-q4mq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.18
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.12
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.8
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.4

## Details
A flaw was found in Moodle. Insufficient capability checks made it possible for a user enrolled in a course to access some details, such as the full name and profile image URL, of other users they did not have permission to access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3640
- https://github.com/moodle/moodle/commit/64a4311266cbe9a9a942c836931bef224018b77d
- https://access.redhat.com/security/cve/CVE-2025-3640
- https://bugzilla.redhat.com/show_bug.cgi?id=2359734
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=467601
