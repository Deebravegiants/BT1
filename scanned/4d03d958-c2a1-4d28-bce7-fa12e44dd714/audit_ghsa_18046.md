# [M] Liferay Portal Vulnerable to Cross-Site Scripting through URLs

## Summary
Severity: Medium
Advisory: GHSA-3fp2-6mwq-4q3j
CVE: CVE-2025-43742
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-3fp2-6mwq-4q3j
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.layout.type.controller.display.page` — affected >=0 <3.0.59

## Details
A reflected cross-site scripting (XSS) vulnerability in the Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.3, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.14 and 7.4 GA through update 92 allows an remote non-authenticated attacker to inject JavaScript in web content for friendly urls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43742
- https://github.com/liferay/liferay-portal/commit/9bd2ae22416d20f5e8ce2800ea96993c7df98f95
- https://github.com/liferay/liferay-portal/commit/f2621572ca5abfe46bad0dca2fa4836deeefa000
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18192
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43742
