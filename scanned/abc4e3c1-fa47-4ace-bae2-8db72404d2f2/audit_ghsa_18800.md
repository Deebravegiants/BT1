# [M] Liferay has Incorrect Permission Assignment for Critical Resource

## Summary
Severity: Medium
Advisory: GHSA-j4f7-gj7q-xg9m
CVE: CVE-2025-62251
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-10-14
Source: https://github.com/advisories/GHSA-j4f7-gj7q-xg9m
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.site.navigation.menu.item.asset.vocabulary` — affected >=0 <1.0.23

## Details
Liferay Portal 7.3.0 through 7.4.3.119, and Liferay DXP 2023.Q3.1 through 2023.Q3.8, 2023.Q4.0 through 2023.Q4.5, 7.4 GA through update 92 and 7.3 GA though update 36 shows content to users who do not have permission to view it via the Menu Display Widget. This security flaw could result in sensitive information being exposed to unauthorized users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62251
- https://github.com/liferay/liferay-portal/commit/12bec829da315c21fbc96492ffbdda4c7a2e59cb
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18236
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62251
