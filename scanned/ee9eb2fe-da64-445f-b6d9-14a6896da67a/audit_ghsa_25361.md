# [M] Liferay Portal and Liferay DXP Vulnerable to Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-9995-qvcg-x7g6
CVE: CVE-2021-33332
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9995-qvcg-x7g6
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.1.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp7

## Details
Cross-site scripting (XSS) vulnerability in the Portlet Configuration module in Liferay Portal 7.1.0 through 7.3.2, and Liferay DXP 7.1 before fix pack 19, and 7.2 before fix pack 7, allows remote attackers to inject arbitrary web script or HTML via the _com_liferay_portlet_configuration_css_web_portlet_PortletConfigurationCSSPortlet_portletResource parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33332
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17053
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120748366
