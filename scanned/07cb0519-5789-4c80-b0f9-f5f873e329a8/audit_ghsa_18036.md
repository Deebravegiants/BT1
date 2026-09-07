# [M] Liferay Portal 7.4.0 and Liferay DXP have a reflected cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m5c7-5gv3-hcpf
CVE: CVE-2025-43734
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-m5c7-5gv3-hcpf
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.q4.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.q3.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.q2.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2024.q1.0 <2024.q1.17
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2025.q1.0 <2025.q1.11
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0
- Maven: `com.liferay:com.liferay.frontend.taglib.clay` — affected >=0 <15.2.2

## Details
A reflected cross-site scripting (XSS) vulnerability in the Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.10, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.1 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.16 and 7.4 GA through update 92 allows a remote authenticated attacker to inject JavaScript code in the “first display label” field in the configuration of a custom sort widget. This malicious payload is then reflected and executed by clay button taglib when refreshing the page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43734
- https://github.com/liferay/liferay-portal/commit/b4ca1bb0961cc1f230508e072c30815eabce062f
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18234
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43734
