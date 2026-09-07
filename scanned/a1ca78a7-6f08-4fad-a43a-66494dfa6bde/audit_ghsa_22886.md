# [H] Moodle CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-wv9c-pfpm-4wc5
CVE: CVE-2019-10186
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wv9c-pfpm-4wc5
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.7.0 <3.7.1
- Packagist: `moodle/moodle` — affected >=3.6.0 <3.6.5
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.7

## Details
A flaw was found in moodle before versions 3.7.1, 3.6.5, 3.5.7. A sesskey (CSRF) token was not being utilised by the XML loading/unloading admin tool.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10186
- https://github.com/moodle/moodle/commit/ea1ac3c7efbddbdb210ea4c75e7156c7d7ee914b
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10186
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=388567#p1566329
- https://web.archive.org/web/20210125055044/https://www.securityfocus.com/bid/109175
