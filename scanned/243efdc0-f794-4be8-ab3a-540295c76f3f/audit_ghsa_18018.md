# [M] Liferay Portal Vulnerable to Cross-Site Scripting via assetTagNames Parameter

## Summary
Severity: Medium
Advisory: GHSA-j6p8-g3rj-ghpm
CVE: CVE-2025-43741
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-j6p8-g3rj-ghpm
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1

## Details
A reflected cross-site scripting (XSS) vulnerability in the Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.3, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.14 and 7.4 GA through update 92 allows an remote authenticated attacker to inject JavaScrip in the _com_liferay_users_admin_web_portlet_UsersAdminPortlet_assetTagNames parameter

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43741
- https://github.com/liferay/liferay-portal/commit/264f4f91aa4f8373c5a9cc44420edf1689384cbb
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18193
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43741
