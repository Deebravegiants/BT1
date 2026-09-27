# [M] Liferay Portal JSONWS API endpoint shares sensitive information

## Summary
Severity: Medium
Advisory: GHSA-cv9j-mg9w-v7wm
CVE: CVE-2025-43768
CWE: CWE-201
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-08-23
Source: https://github.com/advisories/GHSA-cv9j-mg9w-v7wm
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <108.1.1

## Details
Liferay Portal 7.4.0 through 7.4.3.131, and Liferay DXP 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.15 and 7.4 GA through update 92 allows authenticated users without any permissions to access sensitive information of admin users using JSONWS APIs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43768
- https://github.com/liferay/liferay-portal/commit/efdbdbce73605ecd13b1a5e60f5186cc59f09c16
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18154
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43768
