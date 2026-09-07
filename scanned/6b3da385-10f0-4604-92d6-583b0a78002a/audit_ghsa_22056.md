# [M] Moodle allows attackers to trigger the generation of arbitrary messages

## Summary
Severity: Medium
Advisory: GHSA-c87j-9rrq-h3j8
CVE: CVE-2014-9060
CWE: CWE-20
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c87j-9rrq-h3j8
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.5.9
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.6
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.3

## Details
The LTI module in Moodle through 2.4.11, 2.5.x before 2.5.9, 2.6.x before 2.6.6, and 2.7.x before 2.7.3 does not properly restrict the parameters used in a return URL, which allows remote attackers to trigger the generation of arbitrary messages via a modified URL, related to mod/lti/locallib.php and mod/lti/return.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9060
- https://github.com/moodle/moodle/commit/15bde5352bd4bdb54105c0fdfd956c9ca420e4c6
- https://github.com/moodle/moodle/commit/339c6eca3c881742178637cb41cc7ebbe4a3b6b0
- https://github.com/moodle/moodle/commit/44e712e9b72a30c6bc01112040854e91f5758605
- https://github.com/moodle/moodle/commit/edc89dfecb3f6891cea019baf2aecce51b3de41a
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=275165
- https://web.archive.org/web/20150914064838/http://www.securitytracker.com/id/1031215
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-47927
- http://openwall.com/lists/oss-security/2014/11/17/11
