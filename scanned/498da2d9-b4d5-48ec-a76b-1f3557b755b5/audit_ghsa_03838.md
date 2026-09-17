# [H] SQL Injection in LibreNMS

## Summary
Severity: High
Advisory: GHSA-878x-85hc-gc4g
CVE: CVE-2019-12465
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2019-10-11
Source: https://github.com/advisories/GHSA-878x-85hc-gc4g
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <1.53

## Details
An issue was discovered in LibreNMS 1.50.1. A SQL injection flaw was identified in the ajax_rulesuggest.php file where the term parameter is used insecurely in a database query for showing columns of a table, as demonstrated by an ajax_rulesuggest.php?debug=1&term= request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12465
- https://www.darkmatter.ae/xen1thlabs/librenms-sql-injection-vulnerability-xl-19-024
