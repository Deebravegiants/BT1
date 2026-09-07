# [M] Liferay Portal and Liferay DXP Vulnerable to Cross-Site Scripting (XSS) in Asset Publisher App

## Summary
Severity: Medium
Advisory: GHSA-jvvx-8g42-9559
CVE: CVE-2021-29051
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jvvx-8g42-9559
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.1 <7.3.6
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.1.10.fp21
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp10
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.fp1

## Details
Cross-site scripting (XSS) vulnerability in the Asset module's Asset Publisher app in Liferay Portal 7.2.1 through 7.3.5, and Liferay DXP 7.1 before fix pack 21, 7.2 before fix pack 10 and 7.3 before fix pack 1 allows remote attackers to inject arbitrary web script or HTML via the _com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_XXXXXXXXXXXX_assetEntryId parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29051
- https://github.com/liferay/liferay-portal
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120743580
- https://web.archive.org/web/20210524223247/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120743580
- http://liferay.com
