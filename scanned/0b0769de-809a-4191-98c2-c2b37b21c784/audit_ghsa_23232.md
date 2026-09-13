# [M] Liferay Portal and Liferay DXP Fails to Sanitize API Data

## Summary
Severity: Medium
Advisory: GHSA-8j5r-9687-88w5
CVE: CVE-2020-13444
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8j5r-9687-88w5
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.0.0 <7.3.2
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.0 <7.0.10.fp92
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp7

## Details
Liferay Portal 7.x before 7.3.2, and Liferay DXP 7.0 before fix pack 92, 7.1 before fix pack 19, and 7.2 before fix pack 7, does not sanitize the information returned by the DDMDataProvider API, which allows remote authenticated users to obtain the password to REST Data Providers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13444
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17009
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/119317396
