# [H] LibreNMS contains an authenticated SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-qp2j-v5jg-hg68
CVE: CVE-2020-36947
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-qp2j-v5jg-hg68
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0

## Details
LibreNMS 1.46 contains an authenticated SQL Injection vulnerability in the MAC accounting graph endpoint that allows remote attackers to extract database information. Attackers can exploit the vulnerability by manipulating the 'sort' parameter with crafted SQL Injection techniques to retrieve sensitive database contents through time-based blind SQL Injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36947
- https://community.librenms.org
- https://github.com/librenms/librenms
- https://www.exploit-db.com/exploits/49246
- https://www.vulncheck.com/advisories/librenms-mac-accounting-graph-authenticated-sql-injection
