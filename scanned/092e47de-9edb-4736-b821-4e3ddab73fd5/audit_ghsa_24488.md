# [C] CodeIgniter arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-2pcj-76hj-xqhm
CVE: CVE-2016-10131
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2pcj-76hj-xqhm
Type: github-advisory

## Affected
- Packagist: `bcit-ci/codeigniter` — affected >=0 <3.1.3

## Details
system/libraries/Email.php in CodeIgniter before 3.1.3 allows remote attackers to execute arbitrary code by leveraging control over the email->from field to insert sendmail command-line arguments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10131
- https://github.com/bcit-ci/CodeIgniter/issues/4844
- https://github.com/bcit-ci/CodeIgniter/issues/4963
- https://github.com/bcit-ci/CodeIgniter/commit/8db01f13809a92bac7bc95b02893175d7654d627
- https://github.com/codeigniter4/framework
- https://www.codeigniter.com/userguide3/changelog.html#bug-fixes-for-3-1-3
- http://www.securityfocus.com/bid/96851
