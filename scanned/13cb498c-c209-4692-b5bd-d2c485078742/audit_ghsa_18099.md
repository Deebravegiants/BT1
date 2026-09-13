# [M] Liferay Portal's unauthenticated users can access loaded files via URL before submitting the object entry

## Summary
Severity: Medium
Advisory: GHSA-mm62-gwj5-j285
CVE: CVE-2025-43758
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-08-22
Source: https://github.com/advisories/GHSA-mm62-gwj5-j285
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.frontend.js.web` — affected >=0 <5.0.125
- Maven: `com.liferay:com.liferay.object.dynamic.data.mapping.form.field.type` — affected >=0 <1.0.65
- Maven: `com.liferay:com.liferay.object.web` — affected >=0 <1.0.219

## Details
Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.5, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.15 and 7.4 GA through update 92 allows unauthenticated users (guests) to access via URL files uploaded by object entry and stored in document_library

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43758
- https://github.com/liferay/liferay-portal/commit/bf036898c413b6733918f4bfeba59896f1abb34a
- https://github.com/liferay/liferay-portal/commit/ff4efcb59b6b9acf548d37787b8d4b3d1126fff8
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18186
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43758
