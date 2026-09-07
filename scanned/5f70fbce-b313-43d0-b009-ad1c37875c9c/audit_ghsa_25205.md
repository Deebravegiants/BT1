# [M] Moodle allows attacks to obtain sensitive information

## Summary
Severity: Medium
Advisory: GHSA-47cw-whh9-j2fq
CVE: CVE-2014-7848
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-47cw-whh9-j2fq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.6
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.3

## Details
lib/phpunit/bootstrap.php in Moodle 2.6.x before 2.6.6 and 2.7.x before 2.7.3 allows remote attackers to obtain sensitive information via a direct request, which reveals the full path in an error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7848
- https://github.com/moodle/moodle/commit/0baf9763636aa4158a45ef2b539d2df0aa0bbd53
- https://github.com/moodle/moodle/commit/1993cc02b6b05f45ff1776813567c6b3f91480f4
- https://github.com/moodle/moodle/commit/84baa6b1417328ef7e4085d0112acc57167d15e4
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=275160
- https://web.archive.org/web/20150914064838/http://www.securitytracker.com/id/1031215
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-47287
- http://openwall.com/lists/oss-security/2014/11/17/11
