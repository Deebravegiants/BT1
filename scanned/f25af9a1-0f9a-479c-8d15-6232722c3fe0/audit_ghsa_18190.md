# [M] Liferay Portal's Organization Selector exposes organization data to remote authenticated users

## Summary
Severity: Medium
Advisory: GHSA-v53g-736w-mgw4
CVE: CVE-2025-43788
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-12
Source: https://github.com/advisories/GHSA-v53g-736w-mgw4
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.organizations.item.selector.web` — affected >=4.0.2 <4.0.22

## Details
The Organization Selector in Liferay Portal 7.4.0 through 7.4.3.124, and Liferay DXP 2024.Q1.1 through 2024.Q1.12 and 7.4 update 81 through update 85 does not check user permission, which allows remote authenticated users to obtain a list of all organizations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43788
- https://github.com/liferay/liferay-portal/commit/730b0840530e2fbd98d482c9f1a1f0f8391a2369
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43788
