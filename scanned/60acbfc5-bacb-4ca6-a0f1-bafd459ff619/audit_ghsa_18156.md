# [M] Liferay Portal is vulnerable to XSS attack through its search bar portlet

## Summary
Severity: Medium
Advisory: GHSA-x5fw-8xgx-q6c9
CVE: CVE-2025-43781
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-x5fw-8xgx-q6c9
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.search.web` — affected >=6.0.125 <6.0.143

## Details
A reflected cross-site scripting (XSS) vulnerability in Liferay Portal 7.4.3.110 through 7.4.3.128, and Liferay DXP 2024.Q3.1 through 2024.Q3.8, 2024.Q2.0 through 2024.Q2.13 and 2024.Q1.1 through 2024.Q1.12 allows remote attackers to inject arbitrary web script or HTML via the URL in search bar portlet

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43781
- https://github.com/liferay/liferay-portal/commit/f6483b5cff5c07b562c52f9eec336b2ebc9eeacd
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18124
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43781
