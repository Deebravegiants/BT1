# [H] Improper Access Control in moodle

## Summary
Severity: High
Advisory: GHSA-vxhx-gmhm-623c
CVE: CVE-2020-25698
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-vxhx-gmhm-623c
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9.0 <3.9.3
- Packagist: `moodle/moodle` — affected >=3.8.0 <3.8.6
- Packagist: `moodle/moodle` — affected >=3.7.0 <3.7.9
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.15

## Details
Users' enrollment capabilities were not being sufficiently checked in Moodle when they are restored into an existing course. This could lead to them unenrolling users without having permission to do so. Versions affected: 3.5 to 3.5.14, 3.7 to 3.7.8, 3.8 to 3.8.5, 3.9 to 3.9.2 and earlier unsupported versions. Fixed in 3.9.3, 3.8.6, 3.7.9, 3.5.15, and 3.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25698
- https://github.com/moodle/moodle/commit/c8ac07fb50fa92eee1d574823fbda09e1b309a63
- https://bugzilla.redhat.com/show_bug.cgi?id=1895419
- https://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-67837
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4NNFCHPPHRJNJROIX6SYMHOC6HMKP3GU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B55KXBVAT45MDASJ3EK6VIGQOYGJ4NH6
- https://moodle.org/mod/forum/discuss.php?d=413935
