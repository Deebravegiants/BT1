# [M] Liferay Portal and Liferay DXP Reveals Data via Forms

## Summary
Severity: Medium
Advisory: GHSA-9fcg-wrp8-qhr4
CVE: CVE-2025-2565
CWE: CWE-201
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-9fcg-wrp8-qhr4
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0 <7.4.3.129
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q3.0 <2024.Q3.1
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q2.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.Q1.1 <2024.Q1.13
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2023.Q4.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2023.Q3.1

## Details
The data exposure vulnerability in Liferay Portal 7.4.0 through 7.4.3.126, and Liferay DXP 2024.Q3.0, 2024.Q2.0 through 2024.Q2.12, 2024.Q1.1 through 2024.Q1.12, 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92 allows an unauthorized user to obtain entry data from forms.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2565
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2025-2565
