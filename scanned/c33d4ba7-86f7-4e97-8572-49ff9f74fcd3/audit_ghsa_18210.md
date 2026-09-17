# [M] Liferay Portal API Allows Authenticated Users to Access Workflow Definitions by Name

## Summary
Severity: Medium
Advisory: GHSA-wr8m-5h2p-4432
CVE: CVE-2025-43782
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-11
Source: https://github.com/advisories/GHSA-wr8m-5h2p-4432
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.workflow.kaleo.runtime.integration.impl` — affected >=5.0.1 <5.0.48

## Details
An Insecure Direct Object Reference (IDOR) vulnerability in Liferay Portal 7.4.0 through 7.4.3.124, and Liferay DXP 2024.Q2.0 through 2024.Q2.7, 2024.Q1.1 through 2024.Q1.12, and 7.4 GA through update 92 allows remote authenticated users to access a workflow definition by name via the API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43782
- https://github.com/liferay/liferay-portal/commit/4e85bafae4c4e17d3f87054d1f1d49a908d79819
- https://github.com/liferay/liferay-portal/commit/720f2d3fde180e5c2971a5d01246dfec36f68131
- https://github.com/liferay/liferay-portal/commit/acf50c712f7f21c2f52db30883486cb885c8bdd0
- https://github.com/liferay/liferay-portal/commit/ad55ef75cb82c8b1ed01f311488475a646481731
- https://github.com/liferay/liferay-portal/commit/b61004c960e10d576634096fccc9f71677df0fbd
- https://github.com/liferay/liferay-portal/commit/c30a8b729e133f7f40277ce7dc350b87d13d49c7
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43782
