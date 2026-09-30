# [H] Liferay Portal does not limit the depth of a GraphQL queries

## Summary
Severity: High
Advisory: GHSA-8c26-xm99-53w7
CVE: CVE-2025-3602
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-8c26-xm99-53w7
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.vulcan.impl` — affected >=0 <5.0.103

## Details
Liferay Portal 7.4.0 through 7.4.3.97, and Liferay DXP 2023.Q3.1 through 2023.Q3.2, 7.4 GA through update 92, 7.3 GA through update 35, and 7.2 fix pack 8 through fix pack 20 does not limit the depth of a GraphQL queries, which allows remote attackers to perform denial-of-service (DoS) attacks on the application by executing complex queries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3602
- https://github.com/liferay/liferay-portal/commit/6c6dad38c9c891ad58cdee9deb2e35432d7e8816
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-3602
