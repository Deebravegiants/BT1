# [M] Liferay Portal vulnerable to cross-site scripting in the related asset selector

## Summary
Severity: Medium
Advisory: GHSA-2856-xf2f-6vrf
CVE: CVE-2025-43811
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-2856-xf2f-6vrf
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.item.selector.web` — affected >=7.0.35 <7.0.52

## Details
Multiple stored cross-site scripting (XSS) vulnerability in the related asset selector in Liferay Portal 7.4.3.50 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.4, 2023.Q3.1 through 2023.Q3.7, and 7.4 update 50 through update 92 allows remote authenticated attackers to inject arbitrary web script or HTML via a crafted payload injected into an asset author’s (1) First Name, (2) Middle Name, or (3) Last Name text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43811
- https://github.com/liferay/liferay-portal/commit/fdf7044813a8acb9536b01904177ddd44151a6f6
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17922
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43811
