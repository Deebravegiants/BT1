# [M] Moodle creates a MoodleMobile web-service token with an infinite lifetime

## Summary
Severity: Medium
Advisory: GHSA-48rq-vj58-2mh6
CVE: CVE-2014-0214
CWE: CWE-287
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-48rq-vj58-2mh6
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.4.10
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.6
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.3

## Details
login/token.php in Moodle through 2.3.11, 2.4.x before 2.4.10, 2.5.x before 2.5.6, and 2.6.x before 2.6.3 creates a MoodleMobile web-service token with an infinite lifetime, which makes it easier for remote attackers to hijack sessions via a brute-force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0214
- https://github.com/moodle/moodle/commit/14c16a416373f68c36b65f4653c0bd076eb0b290
- https://github.com/moodle/moodle/commit/437240b5aa7719f1b8cce1e0f45ac0708c72cc23
- https://github.com/moodle/moodle/commit/679e323aaab2a968b8e87862e1658814645db525
- https://github.com/moodle/moodle/commit/b5b2eab6778bee166e20bc5eec0138d89795ac3d
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=260362
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-43119
- http://openwall.com/lists/oss-security/2014/05/19/1
