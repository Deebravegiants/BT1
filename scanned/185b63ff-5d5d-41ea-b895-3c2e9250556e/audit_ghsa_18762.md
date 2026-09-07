# [M] Liferay Portal and DXP do not properly restrict access to OpenAPI

## Summary
Severity: Medium
Advisory: GHSA-j82q-c85j-xw4w
CVE: CVE-2025-62256
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-j82q-c85j-xw4w
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.security.auth.verifier` — affected >=0 <6.0.26

## Details
Liferay Portal 7.4.0 through 7.4.3.109, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.7, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions does not properly restrict access to OpenAPI in certain circumstances, which allows remote attackers to access the OpenAPI YAML file via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62256
- https://github.com/liferay/liferay-portal/commit/1ec03c02f2e0ecfdf4101c1a7ade5353767e62e3
- https://github.com/liferay/liferay-portal/commit/27b51dbae35bd6e4b415fb33ecf14b2144b5038f
- https://github.com/liferay/liferay-portal/commit/bc6138ce1be22babbd90dc2190f4dbe91c039334
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17884
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62256
