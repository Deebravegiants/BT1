# [M] Liferay Portal exposes sensitive user data through its Freemarker template

## Summary
Severity: Medium
Advisory: GHSA-rggc-gf6w-9q73
CVE: CVE-2025-43825
CWE: CWE-201
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-04
Source: https://github.com/advisories/GHSA-rggc-gf6w-9q73
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.template.freemarker` — affected >=7.0.3 <7.0.60

## Details
A vulnerability in Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.4, 2024.Q4.0 through 2024.Q4.5, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.1 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.12, 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, and 7.4 GA through update 92 allows sensitive user data to be included in the Freemarker template. This weakness permits an unauthorized actor to gain access to, and potentially expose, confidential information that should remain restricted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43825
- https://github.com/liferay/liferay-portal/commit/ff6c9fb24587a0c7bf3c48356a38b3f492670ea0
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18166
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43825
