# [M] Moodle allows attackers to bypass file-management restrictions

## Summary
Severity: Medium
Advisory: GHSA-622h-cjgg-5mx6
CVE: CVE-2015-3181
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-622h-cjgg-5mx6
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.6.11
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.8
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.6

## Details
files/externallib.php in Moodle through 2.5.9, 2.6.x before 2.6.11, 2.7.x before 2.7.8, and 2.8.x before 2.8.6 does not consider the moodle/user:manageownfiles capability before approving a private-file upload, which allows remote authenticated users to bypass intended file-management restrictions by using web services to perform uploads after this capability has been revoked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3181
- https://github.com/moodle/moodle/commit/350397da93c557f577e7d62e7fc3e233792ad171
- https://github.com/moodle/moodle/commit/4b6b64685affa66784fd238c1bbc1eb0651492a0
- https://github.com/moodle/moodle/commit/57d9a750e3da6708dba13513e9b05e84a895ad9f
- https://github.com/moodle/moodle/commit/8e8ee7530427a10e409386657484e9fd5effc438
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=313688
- https://web.archive.org/web/20200228054133/http://www.securityfocus.com/bid/74728
- https://web.archive.org/web/20201030042703/http://www.securitytracker.com/id/1032358
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-49994
- http://openwall.com/lists/oss-security/2015/05/18/1
