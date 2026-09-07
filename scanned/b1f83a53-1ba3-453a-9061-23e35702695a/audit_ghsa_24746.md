# [M] Moodle allows attackers to discover student e-mail addresses

## Summary
Severity: Medium
Advisory: GHSA-r3fc-hx6q-g6cq
CVE: CVE-2016-2151
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r3fc-hx6q-g6cq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.7.13
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.11
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.5
- Packagist: `moodle/moodle` — affected >=3.0.0 <3.0.3

## Details
user/index.php in Moodle through 2.6.11, 2.7.x before 2.7.13, 2.8.x before 2.8.11, 2.9.x before 2.9.5, and 3.0.x before 3.0.3 grants excessive authorization on the basis of the moodle/course:viewhiddenuserfields capability, which allows remote authenticated users to discover student e-mail addresses by leveraging the teacher role and reading a Participants list.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2151
- https://github.com/moodle/moodle/commit/089ab60017cd3207990658fbd37f7f31948539fa
- https://github.com/moodle/moodle/commit/094fddd00f2e8e832e21e80f417c7b88b33a1f27
- https://github.com/moodle/moodle/commit/85380c6b616e82e31115fbb585d37f0e15f8b0b2
- https://github.com/moodle/moodle/commit/8e24a54e526c149469bd77c910876c4489e87841
- https://github.com/moodle/moodle/commit/a0034bb01773e36dffed2a665646f9cc31d68d5b
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=330173
- https://web.archive.org/web/20160424224349/http://www.securitytracker.com/id/1035333
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-52433
- http://www.openwall.com/lists/oss-security/2016/03/21/1
