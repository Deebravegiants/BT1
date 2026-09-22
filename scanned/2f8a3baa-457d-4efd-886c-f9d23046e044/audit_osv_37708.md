# [H] Open Source Point of Sale is Vulnerable to SQL Injection Through its Item Search Functionality

## Summary
Severity: High
Advisory: CVE-2026-32888
Aliases: GHSA-hmjv-wm3j-pfhw
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32888
Type: osv

## Details
Open Source Point of Sale is a web based point-of-sale application written in PHP using CodeIgniter framework. Versions contain an SQL Injection in the Items search functionality. When the custom attribute search feature is enabled (search_custom filter), user-supplied input from the search GET parameter is interpolated directly into a HAVING clause without parameterization or sanitization. This allows an authenticated attacker with basic item search permissions to execute arbitrary SQL queries. A patch did not exist at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32888.json
- https://github.com/opensourcepos/opensourcepos/security/advisories/GHSA-hmjv-wm3j-pfhw
- https://nvd.nist.gov/vuln/detail/CVE-2026-32888
