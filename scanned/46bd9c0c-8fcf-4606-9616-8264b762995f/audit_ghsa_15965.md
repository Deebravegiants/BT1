# [H] Remote code execution in php-heic-to-jpg

## Summary
Severity: High
Advisory: GHSA-g8v9-c8m3-942v
CVE: CVE-2024-48514
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-24
Source: https://github.com/advisories/GHSA-g8v9-c8m3-942v
Type: github-advisory

## Affected
- Packagist: `maestroerror/php-heic-to-jpg` — affected >=0 <1.0.5

## Details
php-heic-to-jpg < 1.0.5 is vulnerable to remote code execution. An attacker who can upload heic images is able to execute code on the remote server via the file name. As a result, the CIA is no longer guaranteed. This affects php-heic-to-jpg below 1.0.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48514
- https://github.com/MaestroError/php-heic-to-jpg/pull/34
- https://advisories.gitlab.com/pkg/composer/maestroerror/php-heic-to-jpg/CVE-2024-48514
- https://github.com/MaestroError/php-heic-to-jpg
- https://github.com/advisories/GHSA-g8v9-c8m3-942v
- https://github.com/marcoris/CVEs/tree/master/CVE-2024-48514
