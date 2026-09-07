# [M] Liferay Portal and Liferay DXP Vulnerable to Cross-Site Scripting (XSS) in Edit Vocabulary Page

## Summary
Severity: Medium
Advisory: GHSA-vpvm-3wfw-5f5c
CVE: CVE-2021-33328
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vpvm-3wfw-5f5c
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.0.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.10.fp0 <7.0.10.fp96
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp20
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp9

## Details
Cross-site scripting (XSS) vulnerability in the Asset module's edit vocabulary page in Liferay Portal 7.0.0 through 7.3.4, and Liferay DXP 7.0 before fix pack 96, 7.1 before fix pack 20, and 7.2 before fix pack 9, allows remote attackers to inject arbitrary web script or HTML via the (1) _com_liferay_journal_web_portlet_JournalPortlet_name or (2) _com_liferay_document_library_web_portlet_DLAdminPortlet_name parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33328
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17100
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120747972
