# [M] Moodle Reflected XSS in mod_data advanced search

## Summary
Severity: Medium
Advisory: GHSA-mj85-3hqq-r6r9
CVE: CVE-2016-2153
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mj85-3hqq-r6r9
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.7 <2.7.13
- Packagist: `moodle/moodle` — affected >=2.8 <2.8.11
- Packagist: `moodle/moodle` — affected >=2.9 <2.9.5
- Packagist: `moodle/moodle` — affected >=3.0 <3.0.3

## Details
Cross-site scripting (XSS) vulnerability in the advanced-search feature in mod_data in Moodle through 2.6.11, 2.7.x before 2.7.13, 2.8.x before 2.8.11, 2.9.x before 2.9.5, and 3.0.x before 3.0.3 allows remote attackers to inject arbitrary web script or HTML via a crafted field in a URL, as demonstrated by a search form field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2153
- https://github.com/moodle/moodle/commit/87e60e529939c60ef5b07d70c37426d359b2e8a2
- https://github.com/moodle/moodle/commit/8f95eac1634b4d84053cef52a03065e620d6adf2
- https://github.com/moodle/moodle/commit/a5fae3b0d21cc85a7ea2d2c2af8c7fc9acf2fd92
- https://github.com/moodle/moodle/commit/de60fc23aeeef5631d5718469124af3257383ead
- https://github.com/moodle/moodle/commit/ead2dd9c161fcfde04ee1fa602e9101a47c53503
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=330175
- https://web.archive.org/web/20160424224349/http://www.securitytracker.com/id/1035333
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-52727
- http://www.openwall.com/lists/oss-security/2016/03/21/1
