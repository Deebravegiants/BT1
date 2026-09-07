# [M] Moodle arbitrary file read vulnerability

## Summary
Severity: Medium
Advisory: GHSA-56r9-72vx-q989
CVE: CVE-2023-28330
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-56r9-72vx-q989
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.1.0 <4.1.2
- Packagist: `moodle/moodle` — affected >=4.0.0 <4.0.7
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.13
- Packagist: `moodle/moodle` — affected >=0 <3.9.20

## Details
Insufficient sanitizing in backup resulted in an arbitrary file read risk. The capability to access this feature is only available to teachers, managers and admins by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28330
- https://github.com/moodle/moodle/commit/493205b6b280633bcbc49d2eaf4f61a52252c26c
- https://bugzilla.redhat.com/show_bug.cgi?id=2179412
- https://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-77204
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3QZN34VSF4HTCW3C3ZP2OZYSLYUKADPF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3QZN34VSF4HTCW3C3ZP2OZYSLYUKADPF
- https://moodle.org/mod/forum/discuss.php?d=445062
