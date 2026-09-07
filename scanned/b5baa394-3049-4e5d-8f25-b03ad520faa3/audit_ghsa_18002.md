# [M] Liferay Portal Stored Cross-Site Scripting Vulnerability via GroupPagesPortlet_type Parameter

## Summary
Severity: Medium
Advisory: GHSA-58cq-8wm2-6m87
CVE: CVE-2025-43755
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-08-21
Source: https://github.com/advisories/GHSA-58cq-8wm2-6m87
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.layout.admin.web` — affected >=0 <5.0.191

## Details
A Stored cross-site scripting vulnerability in the Liferay Portal 7.4.0 t through 7.4.3.132, and Liferay DXP 2025.Q2.0, 2025.Q1.0 through 2025.Q1.13, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.17 and 7.4 GA through update 92 allows an remote authenticated attacker to inject JavaScript into the _com_liferay_layout_admin_web_portlet_GroupPagesPortlet_type parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43755
- https://github.com/liferay/liferay-portal/commit/5db1ab018d71689fc1eaebcbd27c202e9c2b44d9
- https://github.com/liferay/liferay-portal/commit/f91c374d28c478db38006f5c2d1802c2ab55d034
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18238
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43755
