# [H] phpBB vulnerability related to use of "forum id" in circumstances related to a "global announcement."

## Summary
Severity: High
Advisory: GHSA-5cvh-xqhr-5g87
CVE: CVE-2010-1630
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5cvh-xqhr-5g87
Type: github-advisory

## Affected
- Packagist: `phpbb/phpbb` — affected >=0 <3.0.5

## Details
Unspecified vulnerability in posting.php in phpBB before 3.0.5 has unknown impact and attack vectors related to the use of a "forum id" in circumstances related to a "global announcement."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1630
- https://github.com/phpbb/phpbb-app/commit/1758aa38b21f5960ab1b1a241546b34a203051b6
- https://github.com/phpbb/phpbb-app
- http://github.com/phpbb/phpbb3/commit/4ea3402f9363c9259881bc8ea6ce7fc6cb212657
- http://www.openwall.com/lists/oss-security/2010/05/16/1
- http://www.openwall.com/lists/oss-security/2010/05/18/12
- http://www.openwall.com/lists/oss-security/2010/05/19/5
- http://www.phpbb.com/community/viewtopic.php?f=14&p=9764445
