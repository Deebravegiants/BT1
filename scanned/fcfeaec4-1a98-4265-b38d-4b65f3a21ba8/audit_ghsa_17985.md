# [M] Liferay Portal Reflected Cross-Site Scripting Vulnerability in displayType Parameter

## Summary
Severity: Medium
Advisory: GHSA-cwgh-r52j-xh6c
CVE: CVE-2025-43738
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-cwgh-r52j-xh6c
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.expando.web` — affected >=0

## Details
A reflected cross-site scripting (XSS) vulnerability in the Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q2.0 through 2025.Q2.8, 2025.Q1.0 through 2025.Q1.15, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.1 through 2024.Q2.13 and 2024.Q1.1 through 2024.Q1.19 allows a remote authenticated user to inject JavaScript code via _com_liferay_expando_web_portlet_ExpandoPortlet_displayType parameter.

Liferay Portal is fixed on the master branch from commit acc4771.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43738
- https://github.com/liferay/liferay-portal/commit/acc477143b50de2138854548bc5bad06677e708a
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18290
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43738
