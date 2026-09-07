# [H] Moodle Portfolio script allows instantiation of class chosen by user

## Summary
Severity: High
Advisory: GHSA-vxqh-mx28-7ghw
CVE: CVE-2018-1137
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vxqh-mx28-7ghw
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.1 <3.1.12
- Packagist: `moodle/moodle` — affected >=3.2 <3.2.9
- Packagist: `moodle/moodle` — affected >=3.3 <3.3.6
- Packagist: `moodle/moodle` — affected >=3.4 <3.4.3

## Details
An issue was discovered in Moodle 3.x. By substituting URLs in portfolios, users can instantiate any class. This can also be exploited by users who are logged in as guests to create a DDoS attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1137
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=371204
- http://www.securityfocus.com/bid/104307
