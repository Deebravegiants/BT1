# [M] Liferay Portal and Liferay DXP vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-c6g5-g6r7-q4j6
CVE: CVE-2025-4655
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-08-09
Source: https://github.com/advisories/GHSA-c6g5-g6r7-q4j6
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2025.Q1.0 <2025.Q1.6
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q4.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q3.1
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q2.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q1.0 <2024.Q1.16
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0

## Details
An SSRF vulnerability in FreeMarker templates in Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.5, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.15, and 7.4 GA through update 92 allows template editors to bypass access validations via crafted URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4655
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-4655
