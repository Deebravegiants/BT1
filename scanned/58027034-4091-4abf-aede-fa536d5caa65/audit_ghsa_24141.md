# [M] Liferay Portal and Liferay DXP Fails to Properly Check User Permissions

## Summary
Severity: Medium
Advisory: GHSA-g37f-j8hh-736f
CVE: CVE-2021-33334
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g37f-j8hh-736f
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.0.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.10.fp0 <7.0.10.fp94
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp6

## Details
The Dynamic Data Mapping module in Liferay Portal 7.0.0 through 7.3.2, and Liferay DXP 7.0 before fix pack 94, 7.1 before fix pack 19, and 7.2 before fix pack 6, does not properly check user permissions, which allows remote attackers with the forms "Access in Site Administration" permission to view all forms and form entries in a site via the forms section in site administration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33334
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17039
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120748332
