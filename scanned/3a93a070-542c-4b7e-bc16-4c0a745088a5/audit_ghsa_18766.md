# [M] Liferay Portal Vulnerable to Information Exposure Through a Log File Vulnerability in LDAP Import Feature

## Summary
Severity: Medium
Advisory: GHSA-cw79-fq4f-9r96
CVE: CVE-2025-62262
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-27
Source: https://github.com/advisories/GHSA-cw79-fq4f-9r96
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.security.ldap.impl` — affected >=4.0.2 <4.0.54

## Details
Information exposure through log file vulnerability in LDAP import feature in Liferay Portal 7.4.0 through 7.4.3.97, and older unsupported versions, and Liferay DXP 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows local users to view user email address in the log files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62262
- https://github.com/liferay/liferay-portal/commit/fc14297acd87703ba1027d691fa27a6b96bbb57c
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17826
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62263
