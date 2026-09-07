# [M] Moodle provides calendar-event data without considering whether an activity is hidden

## Summary
Severity: Medium
Advisory: GHSA-h8vc-v44p-5r2q
CVE: CVE-2016-2156
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h8vc-v44p-5r2q
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.7.13
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.11
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.5
- Packagist: `moodle/moodle` — affected >=3.0.0 <3.0.3

## Details
calendar/externallib.php in Moodle through 2.6.11, 2.7.x before 2.7.13, 2.8.x before 2.8.11, 2.9.x before 2.9.5, and 3.0.x before 3.0.3 provides calendar-event data without considering whether an activity is hidden, which allows remote authenticated users to obtain sensitive information via a web-service request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2156
- https://github.com/moodle/moodle/commit/39b851376337b853c8d403dcba64645d16f0a9bd
- https://github.com/moodle/moodle/commit/783e695e00689d67925d6f83722d344c0bd6de94
- https://github.com/moodle/moodle/commit/854e7b8ed0a84eb91ca455ca290427d22bc20baf
- https://github.com/moodle/moodle/commit/c631b112d6e729c84f5d559371a399fe54502ba3
- https://github.com/moodle/moodle/commit/d63ac148b95e5f909618e75efd76f6b5032da158
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=330178
- https://web.archive.org/web/20160424224349/http://www.securitytracker.com/id/1035333
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-52808
- http://www.openwall.com/lists/oss-security/2016/03/21/1
