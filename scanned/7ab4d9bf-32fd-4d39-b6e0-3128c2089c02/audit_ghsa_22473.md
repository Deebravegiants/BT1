# [H] GeniXCMS SQL injection vulnerability

## Summary
Severity: High
Advisory: GHSA-2ppw-6xvg-rwgw
CVE: CVE-2017-5346
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2ppw-6xvg-rwgw
Type: github-advisory

## Affected
- Packagist: `genix/cms` — affected >=0 <1.0.0

## Details
SQL injection vulnerability in `inc/lib/Control/Backend/posts.control.php` in GeniXCMS 0.0.8 allows remote authenticated administrators to execute arbitrary SQL commands via the id parameter to gxadmin/index.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5346
- https://github.com/semplon/GeniXCMS/issues/61
- https://github.com/semplon/GeniXCMS/commit/abfbb6103bfa860275f89d1215ed9c3cba94791e
- https://github.com/GeniXCMS/GeniXCMS
- http://code610.blogspot.com/2017/01/genixcms-sql-injection-quick-autopsy.html
- http://www.securityfocus.com/bid/95655
