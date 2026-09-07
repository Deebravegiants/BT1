# [M] Moodle allows attackers to remove wiki pages

## Summary
Severity: Medium
Advisory: GHSA-p3hj-cfhm-7g6v
CVE: CVE-2014-7837
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p3hj-cfhm-7g6v
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.5.9
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.6
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.3

## Details
mod/wiki/admin.php in Moodle through 2.4.11, 2.5.x before 2.5.9, 2.6.x before 2.6.6, and 2.7.x before 2.7.3 allows remote authenticated users to remove wiki pages by leveraging delete access within a different subwiki.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7837
- https://github.com/moodle/moodle/commit/a481e32f02cdabd2b76aaa06d1d513ffe480e71b
- https://github.com/moodle/moodle/commit/a866ad40beb1c1d7faca2da9c3cbad2dcf6fa32b
- https://github.com/moodle/moodle/commit/dc003ed98e47174a2a4c349f187265a383a386c0
- https://github.com/moodle/moodle/commit/e2a8ac6b1103167d6786cb1801703c2c0f8467ca
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=275163
- https://web.archive.org/web/20150914064838/http://www.securitytracker.com/id/1031215
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-47949
- http://openwall.com/lists/oss-security/2014/11/17/11
