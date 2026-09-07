# [M] Moodle allows attackers to bypass a messaging-disabled setting

## Summary
Severity: Medium
Advisory: GHSA-4jm2-c9jr-6prf
CVE: CVE-2015-0214
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4jm2-c9jr-6prf
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.6.7
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.4
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.2

## Details
message/externallib.php in Moodle through 2.5.9, 2.6.x before 2.6.7, 2.7.x before 2.7.4, and 2.8.x before 2.8.2 allows remote authenticated users to bypass a messaging-disabled setting via a web-services request, as demonstrated by a people-search request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0214
- https://github.com/moodle/moodle/commit/436bbf8975f0daef329c6483ec595dbf9b39ee56
- https://github.com/moodle/moodle/commit/5770e5147838aa06a3ecdff6fc3aebbbd17fff90
- https://github.com/moodle/moodle/commit/c4250ef4f23776ff4862d2860b6be2cf7b2d85f6
- https://github.com/moodle/moodle
- https://github.com/moodle/moodle/commits/v2.6.7#:~:text=MDL%2D48106%20mod_glossary%3A%20Add%20missing%20sesskey%20checks
- https://moodle.org/mod/forum/discuss.php?d=278614
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-48329
- http://openwall.com/lists/oss-security/2015/01/19/1
