# [H] ZoneMinder: Second-Order SQL Injection in `getNearEvents()` via Stored Event Name and Cause Fields

## Summary
Severity: High
Advisory: CVE-2026-27470
Aliases: GHSA-r6gm-478g-f2c4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-21
Source: https://osv.dev/vulnerability/CVE-2026-27470
Type: osv

## Details
ZoneMinder is a free, open source closed-circuit television software application. In versions 1.36.37 and below and 1.37.61 through 1.38.0, there is a second-order SQL Injection vulnerability in the web/ajax/status.php file within the getNearEvents() function. Event field values (specifically Name and Cause) are stored safely via parameterized queries but are later retrieved and concatenated directly into SQL WHERE clauses without escaping. An authenticated user with Events edit and view permissions can exploit this to execute arbitrary SQL queries.

## References
- https://github.com/ZoneMinder/zoneminder/releases/tag/1.36.38
- https://github.com/ZoneMinder/zoneminder/releases/tag/1.38.1
- https://owasp.org/www-community/attacks/SQL_Injection
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27470.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-r6gm-478g-f2c4
- https://nvd.nist.gov/vuln/detail/CVE-2026-27470
