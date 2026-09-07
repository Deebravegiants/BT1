# [M] Liferay Portal Reflected XSS in marketplace-app-manager-web

## Summary
Severity: Medium
Advisory: GHSA-p2f8-vq4r-gqg3
CVE: CVE-2025-4388
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-p2f8-vq4r-gqg3
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.marketplace.app.manager.web` — affected >=0 <5.0.50

## Details
A reflected cross-site scripting (XSS) vulnerability in the Liferay Portal 7.4.0 through 7.4.3.131, and Liferay DXP 2024.Q4.0 through 2024.Q4.5, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.12, 7.4 GA through update 92 allows an remote non-authenticated attacker to inject JavaScript into the modules/apps/marketplace/marketplace-app-manager-web.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4388
- https://github.com/liferay/liferay-portal/commit/0c3ab8936429a1bc48d915fdd801580de592fd9e
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-4388
