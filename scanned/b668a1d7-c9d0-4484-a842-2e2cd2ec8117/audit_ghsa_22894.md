# [M] Moodle is vulnerable to Improper Input Validation in MoodleQuickForm class

## Summary
Severity: Medium
Advisory: GHSA-m63h-q4x3-6hwj
CVE: CVE-2013-2083
CWE: CWE-20
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m63h-q4x3-6hwj
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.2.10
- Packagist: `moodle/moodle` — affected >=2.3.0 <2.3.7
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.4

## Details
The MoodleQuickForm class in `lib/formslib.php` in Moodle through 2.1.10, 2.2.x before 2.2.10, 2.3.x before 2.3.7, and 2.4.x before 2.4.4 does not properly handle a certain array-element syntax, which allows remote attackers to bypass intended form-data filtering via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2083
- https://github.com/moodle/moodle/commit/3c0ba94e879702b3c2f20d4cb4f9120a0bfdd9fc
- https://github.com/moodle/moodle/commit/8a9c3f4951e05eea80775d8c82d00a64434376c7
- https://github.com/moodle/moodle/commit/cc2fb80742af94edde20b6b57da24027f2884a24
- https://github.com/moodle/moodle/commit/d39925c792789230e628548ecff9ca34d0a74c16
- https://github.com/moodle/moodle/commit/d5909fd1447bc6f05dbf37d7c9eb72b79004e24a
- https://github.com/moodle/moodle/commit/e4e1bd900a2fb73e81d761bf8a5b9d2d162073d6
- https://github.com/moodle/moodle/commit/e8ca6884531a3162cf755d7c09c29e7933c84090
- https://github.com/moodle/moodle/commit/eb5852672e5e45fd95b28aab58bad080b15a7b6d
- https://github.com/moodle/moodle/commit/feeb14b9410cac5a9da7437f8cb663e6ada9c9d4
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=228935
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-38885
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/106965.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/106988.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/107026.html
- http://openwall.com/lists/oss-security/2013/05/21/1
