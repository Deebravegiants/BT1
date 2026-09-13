# [H] Liferay Portal has an XXE vulnerability in Java2WsddTask._format

## Summary
Severity: High
Advisory: GHSA-869h-qhfx-w939
CVE: CVE-2024-25606
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-869h-qhfx-w939
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.util.java` — affected >=0 <14.0.0
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.4.3.8
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u12
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u4
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp20

## Details
XXE vulnerability in Liferay Portal 7.2.0 through 7.4.3.7, and older unsupported versions, and Liferay DXP 7.4 before update 4, 7.3 before update 12, 7.2 before fix pack 20, and older unsupported versions allows attackers with permission to deploy widgets/portlets/extensions to obtain sensitive information or consume system resources via the Java2WsddTask._format method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25606
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25606
