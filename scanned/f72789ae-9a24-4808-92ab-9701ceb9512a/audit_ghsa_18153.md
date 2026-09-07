# [M] Liferay Portal exposes ERC which can lead to exploit the time response attack

## Summary
Severity: Medium
Advisory: GHSA-9p7x-8c57-4pqv
CVE: CVE-2025-43786
CWE: CWE-203, CWE-208
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-9p7x-8c57-4pqv
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.vulcan.impl` — affected >=5.0.7 <5.0.127
- Maven: `com.liferay:com.liferay.headless.admin.workflow.impl` — affected >=5.0.4 <5.0.83
- Maven: `com.liferay:com.liferay.portal.workflow.api` — affected >=7.0.1 <11.0.1

## Details
Enumeration of ERC from object entry in Liferay Portal 7.4.0 through 7.4.3.128, and Liferay DXP 2024.Q3.0 through 2024.Q3.1, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.12, 2023.Q4.0 and 7.4 GA through update 92 allow attackers to determine existent ERC in the application by exploit the time response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43786
- https://github.com/liferay/liferay-portal/commit/8f9728086bd61661437b0aa8493c83510914a474
- https://github.com/liferay/liferay-portal/commit/e34499eab2ce1d544835835afe6733a78b4ab532
- https://github.com/liferay/liferay-portal/commit/e4a140d6d92e92911f08fe33051b677742531f19
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18106
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43786
