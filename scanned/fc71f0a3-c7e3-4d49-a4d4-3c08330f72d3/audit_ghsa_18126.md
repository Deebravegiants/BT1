# [M] Liferay Portal and Liferay DXP vulnerable to store Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-rcc7-jx7p-hrv4
CVE: CVE-2025-43776
CWE: CWE-209, CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-rcc7-jx7p-hrv4
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q1.1 <2024.Q1.20
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q2.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q3.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q4.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2025.Q1.0 <2025.Q1.17
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2025.Q2.0 <2025.Q2.10
- Maven: `com.liferay:com.liferay.portal.workflow.web` — affected >=0 <4.0.94

## Details
A stored cross-site scripting vulnerability in the Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q2.0 through 2025.Q2.9, 2025.Q1.0 through 2025.Q1.16, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.19 and 7.4 GA through update 92 allows an remote authenticated attacker to inject JavaScript through Custom Object field label. The malicious payload is stored and executed through Process Builder's Configuration tab without proper escaping.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43776
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18277
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43776
