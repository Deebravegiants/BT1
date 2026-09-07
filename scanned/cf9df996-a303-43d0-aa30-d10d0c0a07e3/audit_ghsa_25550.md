# [M] Improper Authentication in moodle

## Summary
Severity: Medium
Advisory: GHSA-6q9g-3vfq-q2qj
CVE: CVE-2022-0985
CWE: CWE-287, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-6q9g-3vfq-q2qj
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.6
- Packagist: `moodle/moodle` — affected >=3.10.0 <3.10.10
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.13

## Details
Insufficient capability checks could allow users with the moodle/site:uploadusers capability to delete users, without having the necessary moodle/user:delete capability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0985
- https://github.com/moodle/moodle/commit/addd4f894d8173ec8ff0ae2212d51a1977e7bcad
- https://bugzilla.redhat.com/show_bug.cgi?id=2064117
- https://github.com/moodle/moodle
