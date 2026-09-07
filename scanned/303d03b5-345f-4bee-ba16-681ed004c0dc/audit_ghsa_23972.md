# [M] Liferay Portal and Liferay DXP Vulnerable to Cross-Site Scripting (XSS) via Asset Module Parameter

## Summary
Severity: Medium
Advisory: GHSA-9g57-m5vf-qp73
CVE: CVE-2021-29046
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9g57-m5vf-qp73
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected 7.3.5
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.10.fp0 <7.3.10.fp1

## Details
Cross-site scripting (XSS) vulnerability in the Asset module's category selector input field in Liferay Portal 7.3.5 and Liferay DXP 7.3 before fix pack 1, allows remote attackers to inject arbitrary web script or HTML via the _com_liferay_asset_categories_admin_web_portlet_AssetCategoriesAdminPortlet_title parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29046
- https://github.com/liferay/liferay-portal
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120743501
- http://liferay.com
