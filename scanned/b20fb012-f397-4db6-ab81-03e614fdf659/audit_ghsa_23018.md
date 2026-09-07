# [M] Moodle cross-site request forgery (CSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5jph-mvfm-r27p
CVE: CVE-2015-0218
CWE: CWE-352
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5jph-mvfm-r27p
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.6.7
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.4
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.2

## Details
Cross-site request forgery (CSRF) vulnerability in auth/shibboleth/logout.php in Moodle through 2.5.9, 2.6.x before 2.6.7, 2.7.x before 2.7.4, and 2.8.x before 2.8.2 allows remote attackers to hijack the authentication of arbitrary users for requests that trigger a logout.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0218
- https://github.com/moodle/moodle/commit/371d58d70d4ef866f35e33ea6898007112bfe654
- https://github.com/moodle/moodle/commit/693918c30e6b7c95dddd9c5973f98d98342a59d9
- https://github.com/moodle/moodle/commit/b82b4c562b705ea8f11893d9126889bb696b9612
- https://github.com/moodle/moodle/commit/fb60e23a67931eeba8fc9aacf3cc838e462f21f2
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=278618
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-47964
- http://openwall.com/lists/oss-security/2015/01/19/1
