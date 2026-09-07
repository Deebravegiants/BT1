# [M] Moodle has a time restriction bypass

## Summary
Severity: Medium
Advisory: GHSA-w29j-8phw-ffjf
CVE: CVE-2025-62401
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-w29j-8phw-ffjf
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.3
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.7
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.4.11
- Packagist: `moodle/moodle` — affected >=0 <4.1.21

## Details
An issue in Moodle's timed assignment feature allowed students to bypass the time restriction, potentially giving them more time than allowed to complete an assessment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62401
- https://github.com/moodle/moodle/commit/78a3fe6c618676dfc53ea538abbfe35e60674eeb
- https://access.redhat.com/security/cve/CVE-2025-62401
- https://bugzilla.redhat.com/show_bug.cgi?id=2404434
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=470390
