# [H] Liferay Portal vulnerable to user impersonation

## Summary
Severity: High
Advisory: GHSA-qwj8-qgpr-8crm
CVE: CVE-2024-25148
CWE: CWE-200, CWE-201
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-qwj8-qgpr-8crm
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.2
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp15
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u4

## Details
In Liferay Portal 7.2.0 through 7.4.1, and older unsupported versions, and Liferay DXP 7.3 before service pack 3, 7.2 before fix pack 15, and older unsupported versions the `doAsUserId` URL parameter may get leaked when creating linked content using the WYSIWYG editor and while impersonating a user. This may allow remote authenticated users to impersonate a user after accessing the linked content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25148
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25148
