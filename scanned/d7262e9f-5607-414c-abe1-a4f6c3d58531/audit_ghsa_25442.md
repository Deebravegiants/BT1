# [H] Liferay Portal and Liferay DXP Potentially Reveal LDAP Server Password via Unsafe Connection

## Summary
Severity: High
Advisory: GHSA-773f-f929-qgjj
CVE: CVE-2020-15841
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-773f-f929-qgjj
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.3.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.0 <7.0.10.fp89
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp17
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp4

## Details
Liferay Portal before 7.3.0, and Liferay DXP 7.0 before fix pack 89, 7.1 before fix pack 17, and 7.2 before fix pack 4, does not safely test a connection to a LDAP server, which allows remote attackers to obtain the LDAP server's password via the Test LDAP Connection feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15841
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-16928
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/119317439
