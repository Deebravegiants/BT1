# [M] Moodle Improper Privilege Management 

## Summary
Severity: Medium
Advisory: GHSA-xjx9-7c29-pwmm
CVE: CVE-2018-1134
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xjx9-7c29-pwmm
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.1 <3.1.12
- Packagist: `moodle/moodle` — affected >=3.2 <3.2.9
- Packagist: `moodle/moodle` — affected >=3.3 <3.3.6
- Packagist: `moodle/moodle` — affected >=3.4 <3.4.3

## Details
An issue was discovered in Moodle 3.x. Students who submitted assignments and exported them to portfolios can download any stored Moodle file by changing the download URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1134
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=371200
- http://www.securityfocus.com/bid/104307
