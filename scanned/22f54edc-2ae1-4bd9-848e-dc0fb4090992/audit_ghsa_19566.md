# [M] Moodle shows hidden grades to users without permission on some grade reports

## Summary
Severity: Medium
Advisory: GHSA-8m7c-hm88-2p97
CVE: CVE-2025-32045
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-8m7c-hm88-2p97
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.17
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.11
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.7
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.3

## Details
A flaw has been identified in Moodle where insufficient capability checks in certain grade reports allowed users without the necessary permissions to access hidden grades.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-32045
- https://access.redhat.com/security/cve/CVE-2025-32045
- https://bugzilla.redhat.com/show_bug.cgi?id=2356835
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=467086
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-81945
