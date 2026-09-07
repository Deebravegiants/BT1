# [M] Liferay Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qhp6-vp7c-g7xp
CVE: CVE-2025-3760
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-04-17
Source: https://github.com/advisories/GHSA-qhp6-vp7c-g7xp
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.3.132
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.10.fp1
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.10.ep1
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.13.u1
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2023.Q3.1
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2023.Q4.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q1.1 <2024.Q1.13
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q2.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q3.1 <2024.Q3.10
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q4.1 <2025.Q1.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.10
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.10.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected 7.4.13

## Details
A stored cross-site scripting (XSS) vulnerability exists with radio button type custom fields in Liferay Portal 7.2.0 through 7.4.3.129, and Liferay DXP 2024.Q4.1 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.9, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.12, 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, 7.3 GA through update 36, and 7.2 GA through fix pack 20 allows remote authenticated attackers to inject malicious JavaScript into a page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3760
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-3760
