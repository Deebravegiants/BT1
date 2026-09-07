# [H] Liferay Portal Vulnerable to DoS via Crafted Headless API Request

## Summary
Severity: High
Advisory: GHSA-vgqx-447m-wvcj
CVE: CVE-2025-62260
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-vgqx-447m-wvcj
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.100

## Details
Liferay Portal 7.4.0 through 7.4.3.99, and Liferay DXP 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions does not limit the number of objects returned from Headless API requests, which allows remote attackers to perform denial-of-service (DoS) attacks on the application by executing a request that returns a large number of objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62260
- https://github.com/liferay/liferay-portal/commit/5f5c73913b0e7287f7de0b4e19987cc57844b691
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17800
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62260
