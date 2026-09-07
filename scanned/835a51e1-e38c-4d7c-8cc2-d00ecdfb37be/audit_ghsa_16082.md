# [M] Moodle's IDOR in badges allows deletion of arbitrary badges

## Summary
Severity: Medium
Advisory: GHSA-wwjf-gwrv-wh45
CVE: CVE-2024-43431
CWE: CWE-639, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-wwjf-gwrv-wh45
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.12
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.9
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.6
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.2

## Details
A vulnerability was found in Moodle. Insufficient capability checks made it possible to delete badges that a user does not have permission to access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43431
- https://bugzilla.redhat.com/show_bug.cgi?id=2304259
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=461199
