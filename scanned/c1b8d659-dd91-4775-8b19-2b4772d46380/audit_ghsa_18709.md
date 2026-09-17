# [M] Liferay Portal vulnerable to password enumeration

## Summary
Severity: Medium
Advisory: GHSA-8hw3-ghwv-crfh
CVE: CVE-2025-62257
CWE: CWE-307
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-30
Source: https://github.com/advisories/GHSA-8hw3-ghwv-crfh
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.120

## Details
Password enumeration vulnerability in Liferay Portal 7.4.0 through 7.4.3.119, and older unsupported versions, and Liferay DXP 2024.Q1.1 through 2024.Q1.5, 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and older unsupported versions allows remote attackers to determine a user’s password even if account lockout is enabled via brute force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62257
- https://github.com/liferay/liferay-portal/commit/45cffd5030ab78e8b005d9cfd6284311da978c68
- https://github.com/liferay/liferay-portal/commit/924a0a47007665693fe2d29623cb48a426a80266
- https://github.com/liferay/liferay-portal/commit/d21627ac07561c5063f611be631e63ff502ec8e7
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17692
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62257
