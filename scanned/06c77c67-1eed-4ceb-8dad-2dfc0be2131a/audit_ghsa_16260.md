# [M] Authorization Bypass in moodle

## Summary
Severity: Medium
Advisory: GHSA-9r26-5w88-qhp9
CVE: CVE-2024-25983
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-02-19
Source: https://github.com/advisories/GHSA-9r26-5w88-qhp9
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.3
- Packagist: `moodle/moodle` — affected >=4.2.0 <4.2.6
- Packagist: `moodle/moodle` — affected >=0 <4.1.9

## Details
Insufficient checks in a web service made it possible to add comments to the comments block on another user's dashboard when it was not otherwise available (e.g., on their profile page).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25983
- https://github.com/moodle/moodle/commit/4cae44dd0e9a7da47d08d9b75e0ebba0e4b422f4
- https://bugzilla.redhat.com/show_bug.cgi?id=2264099
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KXGBYJ43BUEBUAQZU3DT5I5A3YLF47CB
- https://moodle.org/mod/forum/discuss.php?d=455641
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-78300
