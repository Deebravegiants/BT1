# [M] Moodle Arbitrary File Read via XML External Entity vulnerability

## Summary
Severity: Medium
Advisory: GHSA-27j2-c838-c3qg
CVE: CVE-2014-3543
CWE: CWE-611
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-27j2-c838-c3qg
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.1
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.4
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.7
- Packagist: `moodle/moodle` — affected >=0 <2.4.11

## Details
`mod/imscp/locallib.php` in Moodle through 2.3.11, 2.4.x before 2.4.11, 2.5.x before 2.5.7, 2.6.x before 2.6.4, and 2.7.x before 2.7.1 allows remote attackers to read arbitrary files via a package with a manifest file containing an XML external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue affecting IMSCP resources and the IMSCC format.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3543
- https://github.com/moodle/moodle/commit/595ef4772d330a20c757635ab090acdcc9b2a2fa
- https://git.moodle.org/gw?p=moodle.git;a=commit;h=595ef4772d330a20c757635ab090acdcc9b2a2fa
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=264264
- http://openwall.com/lists/oss-security/2014/07/21/1
