# [H] Liferay Portal and Liferay DXP Vulnerable to Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-v377-8f8f-532h
CVE: CVE-2020-13445
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v377-8f8f-532h
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.3.2
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.0 <7.0.10.fp92
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp18
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp6

## Details
In Liferay Portal before 7.3.2 and Liferay DXP 7.0 before fix pack 92, 7.1 before fix pack 18, and 7.2 before fix pack 6, the template API does not restrict user access to sensitive objects, which allows remote authenticated users to execute arbitrary code via crafted FreeMarker and Velocity templates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13445
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17023
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/119317411
- https://securitylab.github.com/advisories/GHSL-2020-043-liferay_ce
