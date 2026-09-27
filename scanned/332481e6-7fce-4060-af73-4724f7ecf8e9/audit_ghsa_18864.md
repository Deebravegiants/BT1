# [M] Liferay is Vulnerable to Authorization Bypass Through User-Controlled Key

## Summary
Severity: Medium
Advisory: GHSA-pfwq-mr9g-gq6m
CVE: CVE-2025-62252
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-pfwq-mr9g-gq6m
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <99.0.0

## Details
Insecure Direct Object Reference (IDOR) vulnerability in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and older unsupported versions allows remote authenticated users in one virtual instance to assign an organization to a user in a different virtual instance via the _com_liferay_users_admin_web_portlet_UsersAdminPortlet_addUserIds parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62252
- https://github.com/liferay/liferay-portal/commit/8c3fc088f82ffc981a21935e8b6dcf8f36e27152
- https://github.com/liferay/liferay-portal/commit/e7b6074a320a8872ffe9423c3d1a64dada4f3238
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17941
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62252
