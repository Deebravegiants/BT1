# [M] phpMyAdmin path disclosure

## Summary
Severity: Medium
Advisory: GHSA-rmmf-5xhh-gg27
CVE: CVE-2016-9853
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rmmf-5xhh-gg27
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.6.0 <4.6.5
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.4.0 <4.4.15.9

## Details
An issue was discovered in phpMyAdmin. By calling some scripts that are part of phpMyAdmin in an unexpected way, it is possible to trigger phpMyAdmin to display a PHP error message which contains the full path of the directory where phpMyAdmin is installed. During an execution timeout in the export functionality, the errors containing the full path of the directory of phpMyAdmin are written to the export file. All 4.6.x versions (prior to 4.6.5), and 4.4.x versions (prior to 4.4.15.9) are affected. This CVE is for the fopen wrapper issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9853
- https://github.com/phpmyadmin/composer
- https://security.gentoo.org/glsa/201701-32
- https://web.archive.org/web/20210127193655/http://www.securityfocus.com/bid/94527
- https://www.phpmyadmin.net/security/PMASA-2016-63
