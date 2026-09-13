# [M] Liferay Portal users are able to add system admin portlets to pages

## Summary
Severity: Medium
Advisory: GHSA-w3cr-3xw2-rp78
CVE: CVE-2025-43759
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-22
Source: https://github.com/advisories/GHSA-w3cr-3xw2-rp78
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.layout.impl` — affected >=0 <6.0.147

## Details
Liferay Portal versions 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.14 and 7.4 GA through update 92 allows admin users of a virtual instance to add pages that are not in the default/main virtual instance, then any tenant can create a list of all other tenants.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43759
- https://github.com/liferay/liferay-portal/commit/2e29e6733bc0e058bef89d16faac542bf2585346
- https://github.com/liferay/liferay-portal/commit/e8cbc7c27e5ed51c4079dd62738713f31afb46f7
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18185
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43759
