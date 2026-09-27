# [M] Liferay Portal Unvalidated File Upload

## Summary
Severity: Medium
Advisory: GHSA-56qj-wp5r-mvhj
CVE: CVE-2025-43750
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-56qj-wp5r-mvhj
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.dynamic.data.mapping.form.web` — affected >=0 <4.0.180

## Details
Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.1, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.19 and 7.4 GA through update 92 allows remote unauthenticated users (guests) to upload files via the form attachment field without proper validation, enabling extension obfuscation and bypassing MIME type checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43750
- https://github.com/liferay/liferay-portal/commit/7f58439723c8373e038d5060d0bc58ff2475bdc5
- https://github.com/liferay/liferay-portal/commit/b9e57377cb88bad1775beab50558cc2bd5a9758e
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18190
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43750
