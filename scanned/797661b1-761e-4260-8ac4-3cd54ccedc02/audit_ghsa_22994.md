# [C] Joomla! Object Injection Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5m3w-rvvh-8fx6
CVE: CVE-2019-7743
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5m3w-rvvh-8fx6
Type: github-advisory

## Affected
- Packagist: `joomla/joomla-cms` — affected >=2.5.0 <3.9.3

## Details
An issue was discovered in Joomla! before 3.9.3. The phar:// stream wrapper can be used for object injection attacks because there is no protection mechanism (such as the TYPO3 PHAR stream wrapper) to prevent use of the phar:// handler for non .phar-files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7743
- https://github.com/joomla/joomla-cms/issues/23907
- https://developer.joomla.org/security-centre/770-20190206-core-implement-the-typo3-phar-stream-wrapper
- https://github.com/joomla/joomla-cms
- https://web.archive.org/web/20210730211655/https://www.securityfocus.com/bid/107050
