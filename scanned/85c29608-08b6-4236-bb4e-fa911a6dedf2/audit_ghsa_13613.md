# [C] Liferay Portal and Liferay DXP Vulnerable to Stored XSS in the Manage Vocabulary Page

## Summary
Severity: Critical
Advisory: GHSA-g44j-f8wm-6622
CVE: CVE-2023-42629
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-g44j-f8wm-6622
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.asset.categories.admin.web` — affected >=0 <5.0.87
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u88

## Details
Stored cross-site scripting (XSS) vulnerability in the manage vocabulary page in the Asset Categories Admin Web module before 5.0.87 from Liferay Portal (7.4.2 through 7.4.3.87), and Liferay DXP 7.4 before update 88 allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a Vocabulary's 'description' text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42629
- https://github.com/liferay/liferay-portal/commit/2e02110747dd5cccb978623545bfa1f3ad0a5602
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-42629
- https://www.pentagrid.ch/en/blog/stored-cross-site-scripting-vulnerabilities-in-liferay-portal
