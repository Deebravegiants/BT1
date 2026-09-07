# [M] Moodle Portfolio forum caller class allows a user to download any file

## Summary
Severity: Medium
Advisory: GHSA-vxmv-74rf-vqgp
CVE: CVE-2018-1135
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vxmv-74rf-vqgp
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.1 <3.1.12
- Packagist: `moodle/moodle` — affected >=3.2 <3.2.9
- Packagist: `moodle/moodle` — affected >=3.3 <3.3.6
- Packagist: `moodle/moodle` — affected >=3.4 <3.4.3

## Details
An issue was discovered in Moodle 3.x. Students who posted on forums and exported the posts to portfolios can download any stored Moodle file by changing the download URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1135
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=371201
- http://www.securityfocus.com/bid/104307
