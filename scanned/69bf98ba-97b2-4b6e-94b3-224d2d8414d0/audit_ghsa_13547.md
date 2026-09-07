# [C] Liferay Portal and Liferay DXP Vulnerable to XSS in the Wiki Widget

## Summary
Severity: Critical
Advisory: GHSA-hv45-r2f5-fmhj
CVE: CVE-2023-42628
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-hv45-r2f5-fmhj
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.wiki.web` — affected >=0 <7.0.95
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.10.fp83
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u34
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u88

## Details
Stored cross-site scripting (XSS) vulnerability in the Wiki widget in Liferay Wiki Web before 7.0.95 from Liferay Portal (7.1.0 through 7.4.3.87), and Liferay DXP 7.0 fix pack 83 through 102, 7.1 fix pack 28 and earlier, 7.2 fix pack 20 and earlier, 7.3 update 33 and earlier, and 7.4 before update 88 allows remote attackers to inject arbitrary web script or HTML into a parent wiki page via a crafted payload injected into a wiki page's ‘Content’ text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42628
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-42628
- https://www.pentagrid.ch/en/blog/stored-cross-site-scripting-vulnerabilities-in-liferay-portal
