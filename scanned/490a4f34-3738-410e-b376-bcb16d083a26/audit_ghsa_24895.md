# [M] Moodle Allows Unauthenticated Dropbox Access

## Summary
Severity: Medium
Advisory: GHSA-mpjx-8phj-5m34
CVE: CVE-2012-5471
CWE: CWE-287
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mpjx-8phj-5m34
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.3 <2.3.3
- Packagist: `moodle/moodle` — affected >=2.2 <2.2.6
- Packagist: `moodle/moodle` — affected >=2.1 <2.1.9

## Details
The Dropbox Repository File Picker in Moodle 2.1.x before 2.1.9, 2.2.x before 2.2.6, and 2.3.x before 2.3.3 allows remote authenticated users to access the Dropbox of a different user by leveraging an unattended workstation after a logout.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5471
- https://github.com/moodle/moodle/commit/8eb614d4bb4a80ed51520bca528530914082136f
- https://github.com/moodle/moodle/commit/a3433213a1a2346c145e004ab1dc08b58279f910
- https://github.com/moodle/moodle/commit/c62a20c42b96f0195c4de075e5c58a4e7d381428
- https://github.com/moodle/moodle/commit/cd029574b699c74e55fa287f0b4db45d2dcf9fde
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=216155
- https://web.archive.org/web/20121202030020/http://www.securityfocus.com/bid/56505
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-29872
- http://openwall.com/lists/oss-security/2012/11/19/1
