# [M] Liferay Portal Vulnerable to Insecure Direct Object Reference

## Summary
Severity: Medium
Advisory: GHSA-v6xr-v2qg-h22h
CVE: CVE-2025-43732
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-08-18
Source: https://github.com/advisories/GHSA-v6xr-v2qg-h22h
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.roles.selector.web` — affected >=0 <5.0.32

## Details
Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.10, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.1 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.17 and 7.4 GA through update 92 is vulnerable to Insecure Direct Object Reference (IDOR) in the groupId parameter of the _com_liferay_roles_selector_web_portlet_RolesSelectorPortlet_groupId. When an organization administrator modifies this parameter id value, they can gain unauthorized access to user lists from other organizations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43732
- https://github.com/liferay/liferay-portal/commit/1ab3de8142d9201d10d89f5eeb1edeea64599d57
- https://github.com/liferay/liferay-portal/commit/830140e15ccfeb105641681c4f2bb375c12582ba
- https://github.com/liferay/liferay-portal/commit/f07339e42a5788aa44016c4ca566b92399643442
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18221
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43732
