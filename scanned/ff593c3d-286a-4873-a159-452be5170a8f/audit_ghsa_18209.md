# [M] Liferay Portal and DXP does not properly check permission with import and export tasks

## Summary
Severity: Medium
Advisory: GHSA-pm45-xx4q-fmv7
CVE: CVE-2025-43806
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-23
Source: https://github.com/advisories/GHSA-pm45-xx4q-fmv7
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.headless.batch.engine.impl` — affected >=0 <4.0.52
- Maven: `com.liferay:com.liferay.batch.engine.service` — affected >=0 <4.0.102

## Details
Batch Engine in Liferay Portal 7.4.0 through 7.4.3.112, and Liferay DXP 2023.Q4.0 through 2023.Q4.7, 2023.Q3.1 through 2023.Q3.10, and 7.4 GA through update 92 does not properly check permission with import and export tasks, which allows remote authenticated users to access the exported data via the REST APIs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43806
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17957
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43806
