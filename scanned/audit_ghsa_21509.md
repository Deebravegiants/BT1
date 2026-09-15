# [C] Liferay Portal and Liferay DXP Vulnerable to SQL Injection via the Fragment Module

## Summary
Severity: Critical
Advisory: GHSA-r5fj-j449-vqw2
CVE: CVE-2022-42120
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-r5fj-j449-vqw2
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.fragment.service` — affected >=0 <4.0.33
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u4
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u17

## Details
A SQL injection vulnerability in the Fragment module before 4.0.33 from Liferay Portal (7.3.3 through 7.4.3.16), and Liferay DXP 7.3 before update 4, and 7.4 before update 17 allows attackers to execute arbitrary SQL commands via a PortletPreferences' `namespace` attribute.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42120
- https://github.com/liferay/liferay-portal/commit/6f94d203f5a194a64055e1e0ba0224d26ec54e47
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17513
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42120
- https://web.archive.org/web/20220801000000*/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42120
- http://liferay.com
