# [M] Moodle does not check for the moodle/course:viewhiddencourses capability

## Summary
Severity: Medium
Advisory: GHSA-c3vx-v4x8-x894
CVE: CVE-2014-0217
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c3vx-v4x8-x894
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.3

## Details
enrol/index.php in Moodle 2.6.x before 2.6.3 does not check for the moodle/course:viewhiddencourses capability before listing hidden courses, which allows remote attackers to obtain sensitive name and summary information about these courses by leveraging the guest role and visiting a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0217
- https://github.com/moodle/moodle/commit/eaea796e70f6630494d3772684604ab6e907f4ac
- https://github.com/moodle/moodle/commit/fcf199e7a13e453bfe3855c6946e8357fcbdef92
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=260365
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-45126
- http://openwall.com/lists/oss-security/2014/05/19/1
