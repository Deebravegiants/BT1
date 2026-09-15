# [M] baserCMS has an SQL injection vulnerability in its blog post functionality

## Summary
Severity: Medium
Advisory: GHSA-vh89-rjph-2g7p
CVE: CVE-2026-27697
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-vh89-rjph-2g7p
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <5.2.3

## Details
baserCMS has a SQL injection vulnerability in blog posts.

### Target
baserCMS 5.2.2 and earlier versions

### Vulnerability

Malicious SQL may be executed in blog posts.

### Countermeasures
Update to the latest version of baserCMS

Please refer to the following page to reference for more information.
https://basercms.net/security/JVN_52157568

### Credits

Mirai Matsumoto@Future Secure Wave, Inc.

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-vh89-rjph-2g7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-27697
- https://basercms.net/security/JVN_20837860
- https://github.com/baserproject/basercms
- https://github.com/baserproject/basercms/releases/tag/5.2.3
