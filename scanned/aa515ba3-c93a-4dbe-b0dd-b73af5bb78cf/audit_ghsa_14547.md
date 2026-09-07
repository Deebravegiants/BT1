# [M] Moodle may allow teachers to access the names of users they could not otherwise access

## Summary
Severity: Medium
Advisory: GHSA-prjm-2fj2-787f
CVE: CVE-2023-28336
CWE: CWE-200, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-prjm-2fj2-787f
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.1.0 <4.1.2
- Packagist: `moodle/moodle` — affected >=4.0.0 <4.0.7
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.13
- Packagist: `moodle/moodle` — affected >=0 <3.9.20

## Details
Insufficient filtering of grade report history made it possible for teachers to access the names of users they could not otherwise access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28336
- https://github.com/moodle/moodle/commit/a931a7f8cec3657827268837b27962a13817ca2b
- https://bugzilla.redhat.com/show_bug.cgi?id=2179426
- https://git.moodle.org/gw?p=moodle.git;a=commit;h=a931a7f8cec3657827268837b27962a13817ca2b
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3QZN34VSF4HTCW3C3ZP2OZYSLYUKADPF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3QZN34VSF4HTCW3C3ZP2OZYSLYUKADPF
- https://moodle.org/mod/forum/discuss.php?d=445068
