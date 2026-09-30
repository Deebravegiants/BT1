# [M] Liferay Portal is vulnerable to DNS rebinding attacks

## Summary
Severity: Medium
Advisory: GHSA-f5vh-4rj2-w8r8
CVE: CVE-2025-62266
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-30
Source: https://github.com/advisories/GHSA-f5vh-4rj2-w8r8
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.110

## Details
By default, Liferay Portal 7.4.0 through 7.4.3.119, and older unsupported versions, and Liferay DXP 2024.Q1.1 through 2024.Q1.5, 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and older unsupported versions is vulnerable to DNS rebinding attacks, which allows remote attackers to redirect users to arbitrary external URLs. This vulnerability can be mitigated by changing the redirect URL security from IP to domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62266
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62256
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62257
