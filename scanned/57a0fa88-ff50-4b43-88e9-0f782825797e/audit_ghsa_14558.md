# [M] Moodle may display roles to users who don't have access to them

## Summary
Severity: Medium
Advisory: GHSA-vj5p-fp42-774p
CVE: CVE-2023-1402
CWE: CWE-200, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-vj5p-fp42-774p
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.1.0 <4.1.2
- Packagist: `moodle/moodle` — affected >=4.0.0 <4.0.7
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.13
- Packagist: `moodle/moodle` — affected >=0 <3.9.20

## Details
The course participation report required additional checks to prevent roles being displayed which the user did not have access to view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1402
- https://github.com/moodle/moodle/commit/f0a557bffbdb450648d0e4cedb391d14d8a0a253
- https://bugzilla.redhat.com/show_bug.cgi?id=2179427
- https://git.moodle.org/gw?p=moodle.git;a=commitdiff;h=f0a557bffbdb450648d0e4cedb391d14d8a0a253
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3QZN34VSF4HTCW3C3ZP2OZYSLYUKADPF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3QZN34VSF4HTCW3C3ZP2OZYSLYUKADPF
- https://moodle.org/mod/forum/discuss.php?d=445069
