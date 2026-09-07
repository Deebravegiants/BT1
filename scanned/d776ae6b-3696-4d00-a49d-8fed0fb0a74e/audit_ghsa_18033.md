# [M] Liferay Portal CSRF Vulnerability via Endpoint Parameter

## Summary
Severity: Medium
Advisory: GHSA-7q33-gwcm-r6cj
CVE: CVE-2025-43745
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-7q33-gwcm-r6cj
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1

## Details
A CSRF vulnerability in Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q2.0 through 2025.Q2.7, 2025.Q1.0 through 2025.Q1.14, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.19 and 7.4 GA through update 92 allows remote attackers to performs cross-origin request on behalf of the authenticated user via the endpoint parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43745
- https://github.com/liferay/liferay-portal/commit/037b58f96c9ded47960ab493a68d68aaf32b1a43
- https://github.com/liferay/liferay-portal/commit/2387ee78fd471ea1c1c4d696aa0cbb1bce72665e
- https://github.com/liferay/liferay-portal/commit/729dfc202c9d2724b5f3f749ead14eb13832e101
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18275
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43745
