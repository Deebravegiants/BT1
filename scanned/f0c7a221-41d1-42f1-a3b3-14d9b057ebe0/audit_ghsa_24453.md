# [M] Moodle does not enforce the forceloginforprofiles setting

## Summary
Severity: Medium
Advisory: GHSA-8r7x-qq55-74v2
CVE: CVE-2013-1830
CWE: CWE-284
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8r7x-qq55-74v2
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0
- Packagist: `moodle/moodle` — affected >=2.2.0 <2.2.8
- Packagist: `moodle/moodle` — affected >=2.3.0 <2.3.5
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.2

## Details
`user/view.php` in Moodle through 2.1.10, 2.2.x before 2.2.8, 2.3.x before 2.3.5, and 2.4.x before 2.4.2 does not enforce the `forceloginforprofiles` setting, which allows remote attackers to obtain sensitive course-profile information by leveraging the guest role, as demonstrated by a Google search.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1830
- https://github.com/moodle/moodle/commit/3ecc63e9dbe29c6a5a8f65fa8e7980ba0fffb5a8
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=225341
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-37481
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101310.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101358.html
- http://openwall.com/lists/oss-security/2013/03/25/2
