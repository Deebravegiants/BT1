# [M] Liferay Portal exposes 500 status when attempting login with a deleted client secret

## Summary
Severity: Medium
Advisory: GHSA-9vwq-j6gq-w9xh
CVE: CVE-2025-43777
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-9vwq-j6gq-w9xh
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.security.sso.openid.connect.impl` — affected >=6.0.4 <7.0.48

## Details
Liferay Portal  7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q2.0 through 2025.Q2.9, 2025.Q1.0 through 2025.Q1.16, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13 and 2024.Q1.1 through 2024.Q1.19 exposes "Internal Server Error" in the response body when a login attempt is made with a deleted Client Secret.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43777
- https://github.com/liferay/liferay-portal/commit/e4ae0e49dd90485f2f2d8d07ab972da5aba7fa45
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43777
