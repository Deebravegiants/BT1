# [H] SQL injection in Liferay Portal

## Summary
Severity: High
Advisory: GHSA-g7vw-43xg-8m4h
CVE: CVE-2023-33945
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-g7vw-43xg-8m4h
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.1 <7.4.3.18

## Details
SQL injection vulnerability in the upgrade process for SQL Server in Liferay Portal 7.3.1 through 7.4.3.17, and Liferay DXP 7.3 before update 6, and 7.4 before update 18 allows attackers to execute arbitrary SQL commands via the name of a database table's primary key index. This vulnerability is only exploitable when chained with other attacks. To exploit this vulnerability, the attacker must modify the database and wait for the application to be upgraded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33945
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-33945
