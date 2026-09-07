# [M] Moodle allows attackers to bypass a forced-password-change requirement

## Summary
Severity: Medium
Advisory: GHSA-5659-g9p4-354f
CVE: CVE-2015-2272
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5659-g9p4-354f
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.6.9
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.6
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.4

## Details
login/token.php in Moodle through 2.5.9, 2.6.x before 2.6.9, 2.7.x before 2.7.6, and 2.8.x before 2.8.4 allows remote authenticated users to bypass a forced-password-change requirement by creating a web-services token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2272
- https://github.com/moodle/moodle/commit/0899c0adc036e34e0c37ea1a8d3551610cdb4233
- https://github.com/moodle/moodle/commit/6e284d55b234287169f21e6ef8a9a237d6eedfe4
- https://github.com/moodle/moodle/commit/b0abcbda170b57649e0ed39ac5aca91dbc30337f
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=307386
- https://web.archive.org/web/20200227182455/http://www.securityfocus.com/bid/73166
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-48691
- http://www.securityfocus.com/bid/73166
