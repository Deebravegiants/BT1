# [M] Liferay Portal and Liferay DXP User Enumeration Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qm43-g2xj-hvg5
CVE: CVE-2024-26268
CWE: CWE-203
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-qm43-g2xj-hvg5
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.3.27-ga27
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp20
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u8
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u27

## Details
User enumeration vulnerability in Liferay Portal 7.2.0 through 7.4.3.26, and older unsupported versions, and Liferay DXP 7.4 before update 27, 7.3 before update 8, 7.2 before fix pack 20, and older unsupported versions allows remote attackers to determine if an account exist in the application by comparing the request's response time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-26268
- https://github.com/liferay/liferay-portal/commit/46db55ec21103fa39542e2cba080c4f98e3c5f93
- https://github.com/liferay/liferay-portal/commit/d8d0ae0178a2d902b541c80a230a2c7a5ab246e8
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-26268
