# [M] Moodle XSS from profile fields from external db

## Summary
Severity: Medium
Advisory: GHSA-6mxm-wpqv-675h
CVE: CVE-2016-2152
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6mxm-wpqv-675h
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.7 <2.7.13
- Packagist: `moodle/moodle` — affected >=2.8 <2.8.11
- Packagist: `moodle/moodle` — affected >=2.9 <2.9.5
- Packagist: `moodle/moodle` — affected >=3.0 <3.0.3

## Details
Multiple cross-site scripting (XSS) vulnerabilities in auth/db/auth.php in Moodle through 2.6.11, 2.7.x before 2.7.13, 2.8.x before 2.8.11, 2.9.x before 2.9.5, and 3.0.x before 3.0.3 allow remote attackers to inject arbitrary web script or HTML via an external DB profile field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2152
- https://github.com/moodle/moodle/commit/3b214760fb51ae2b0c85bbb2b272b9bc7c164657
- https://github.com/moodle/moodle/commit/4db8407d3eaba17a8d3f81957b8e93e9f2554055
- https://github.com/moodle/moodle/commit/4ee7394c8bfa95a63428385b542c2066cd2d8ea1
- https://github.com/moodle/moodle/commit/54d6ee8c0874d72705ffa4c7c17d7c90bc16c897
- https://github.com/moodle/moodle/commit/61da84e4148aa1de83a6389eb77abf3bbf09a349
- https://github.com/moodle/moodle/commit/82d0c0b5218e9ceb35a4e24b4a4e1e2e9cfc840c
- https://github.com/moodle/moodle/commit/ce597604763272396e5cb8ec93859a8568020b8b
- https://github.com/moodle/moodle/commit/d9d8e9c3fe92c5f25e319a38fe5617088965ad20
- https://github.com/moodle/moodle/commit/f4fcb1c4f76488d4571d3d265efce3813676c45d
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=330174
- https://web.archive.org/web/20160424224349/http://www.securitytracker.com/id/1035333
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-50705
- http://www.openwall.com/lists/oss-security/2016/03/21/1
