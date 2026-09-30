# [M] Liferay Portal Unauthenticated File Access via URL

## Summary
Severity: Medium
Advisory: GHSA-5fx5-cff6-f3fp
CVE: CVE-2025-43749
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-5fx5-cff6-f3fp
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1

## Details
Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.1, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.14 and 7.4 GA through update 92 allows unauthenticated users (guests) to access via URL files uploaded in the form and stored in document_library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43749
- https://github.com/liferay/liferay-portal/commit/5919534a979a97444172f49705b7a224e372e625
- https://github.com/liferay/liferay-portal/commit/b88e7e0912d27cc166fc788b642616ece9e8c484
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18176
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43749
