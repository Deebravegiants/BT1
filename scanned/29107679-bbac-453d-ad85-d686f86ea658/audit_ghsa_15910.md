# [C] Liferay Portal and Liferay DXP Workflow Component Does Not Check User Permissions

## Summary
Severity: Critical
Advisory: GHSA-3mfq-fp2f-vwqh
CVE: CVE-2024-38002
CWE: CWE-862, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-22
Source: https://github.com/advisories/GHSA-3mfq-fp2f-vwqh
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.2-ga3 <7.4.3.112-ga112
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2023.Q4.0 <2023.Q4.6
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2023.Q3.1 <2023.Q3.9
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3-ga <7.3.10.u36
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4-ga <7.4.13.u92

## Details
The workflow component in Liferay Portal 7.3.2 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, 7.4 GA through update 92 and 7.3 GA through update 36 does not properly check user permissions before updating a workflow definition, which allows remote authenticated users to modify workflow definitions and execute arbitrary code (RCE) via the headless API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38002
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2024-38002
