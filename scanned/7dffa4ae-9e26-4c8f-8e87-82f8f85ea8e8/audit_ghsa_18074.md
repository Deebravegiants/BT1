# [M] Liferay Portal Vulnerable to Cross-Site Scripting via DDM Structure Field Labels

## Summary
Severity: Medium
Advisory: GHSA-m49p-6cjp-x2h3
CVE: CVE-2025-43744
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-m49p-6cjp-x2h3
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1

## Details
A stored DOM-based Cross-Site Scripting (XSS) vulnerability in Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q2.0 through 2025.Q2.5, 2025.Q1.0 through 2025.Q1.15, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.19 and 7.4 GA through update 92 exists in the Asset Publisher configuration UI within the Source.js module. This vulnerability allows attackers to inject arbitrary JavaScript via DDM structure field labels which are then inserted into the DOM using innerHTML without proper encoding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43744
- https://github.com/liferay/liferay-portal/commit/3b36fadfe92437deab4a55029a1a369e046f3829
- https://github.com/liferay/liferay-portal/commit/c07a490b3d3759f38c5473cda74e99540bd0235e
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18271
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43744
