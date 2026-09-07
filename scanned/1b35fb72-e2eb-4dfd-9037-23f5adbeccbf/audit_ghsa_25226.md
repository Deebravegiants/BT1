# [H] phpBB Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-h3mr-q96r-37v4
CVE: CVE-2018-19274
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h3mr-q96r-37v4
Type: github-advisory

## Affected
- Packagist: `phpbb/phpbb` — affected >=0 <3.2.4

## Details
Passing an absolute path to a file_exists check in phpBB before 3.2.4 allows Remote Code Execution through Object Injection by employing Phar deserialization when an attacker has access to the Admin Control Panel with founder permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19274
- https://blog.ripstech.com/2018/phpbb3-phar-deserialization-to-remote-code-execution
- https://github.com/phpbb/phpbb-app
- https://lists.debian.org/debian-lts-announce/2018/11/msg00029.html
- https://www.phpbb.com/community/viewtopic.php?f=14&t=2492206
