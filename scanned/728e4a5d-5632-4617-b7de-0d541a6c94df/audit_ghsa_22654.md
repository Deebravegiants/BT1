# [H] LibreNMS SQL Injection

## Summary
Severity: High
Advisory: GHSA-4fwh-r866-pvh9
CVE: CVE-2018-20678
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4fwh-r866-pvh9
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <1.65

## Details
LibreNMS through 1.47 allows SQL injection via the html/ajax_table.php sort[hostname] parameter, exploitable by authenticated users during a search.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20678
- https://github.com/librenms/librenms/pull/11920
- https://github.com/librenms/librenms/commit/32f72bc1ab7e980e4070e826a89d0d36a5ba62dd
- https://cert.enea.pl/advisories/cert-190101.html
