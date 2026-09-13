# [M] Liferay Portal and Liferay DXP Fails to Check User Permissions for Workflow Submissions

## Summary
Severity: Medium
Advisory: GHSA-g7xc-m762-wg8f
CVE: CVE-2021-33333
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g7xc-m762-wg8f
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.0.10.fp93
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp6

## Details
The Portal Workflow module in Liferay Portal 7.3.2 and earlier, and Liferay DXP 7.0 before fix pack 93, 7.1 before fix pack 19 and 7.2 before fix pack 6, does not properly check user permission, which allows remote authenticated users to view and delete workflow submissions via crafted URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33333
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17032
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120747742
