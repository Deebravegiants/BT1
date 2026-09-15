# [M] Gila CMS SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-rpjw-97p8-p2xp
CVE: CVE-2020-26623
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-rpjw-97p8-p2xp
Type: github-advisory

## Affected
- Packagist: `gilacms/gila` — affected >=0

## Details
SQL Injection vulnerability discovered in Gila CMS 1.15.4 and earlier allows a remote attacker to execute arbitrary web scripts via the Area parameter under the Administration>Widget tab after the login portal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26623
- https://github.com/GilaCMS/gila
- https://github.com/GilaCMS/gila/security/policy
- https://packetstormsecurity.com/files/176301/GilaCMS-1.15.4-SQL-Injection.html
- http://gilacms.com
