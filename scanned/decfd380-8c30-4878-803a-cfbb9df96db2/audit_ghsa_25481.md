# [M] Liferay Portal and Liferay DXP Bypass via Double Encoded URL

## Summary
Severity: Medium
Advisory: GHSA-vrwx-q9pj-x488
CVE: CVE-2020-15840
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vrwx-q9pj-x488
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=7.2.0 <7.4.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.0.10.fp93
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp7
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.3.1
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <7.1.3

## Details
In Liferay Portal before 7.3.1, com.liferay.portal:com.liferay.portal.impl before 7.1.3 and 7.4.0, Liferay Portal 6.2 EE, and Liferay DXP 7.2, DXP 7.1 and DXP 7.0, the property 'portlet.resource.id.banned.paths.regexp' can be bypassed with doubled encoded URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15840
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17046
- https://portal.liferay.dev/learn/security/known-vulnerabilities
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/119772204
- https://security.snyk.io/vuln/SNYK-JAVA-COMLIFERAYPORTAL-1296538
