# [M] Craft CMS Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3jxh-789f-p7m6
CVE: CVE-2021-27902
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-3jxh-789f-p7m6
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=0 <3.6.0

## Details
An issue was discovered in Craft CMS before 3.6.0. In some circumstances, a potential XSS vulnerability existed in connection with front-end forms that accepted user uploads.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27902
- https://github.com/craftcms/cms/commit/8ee85a8f03c143fa2420e7d6f311d95cae3b19ce
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#360---2021-01-26
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#security-1
