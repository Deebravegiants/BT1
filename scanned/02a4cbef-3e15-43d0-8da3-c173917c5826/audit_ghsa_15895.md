# [H] Liferay Portal and Liferay DXP Vulnerable to Cross-Site Request Forgery (CSRF) via the Content Page Editor

## Summary
Severity: High
Advisory: GHSA-p63m-vmjr-wg37
CVE: CVE-2024-26272
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-22
Source: https://github.com/advisories/GHSA-p63m-vmjr-wg37
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.2 <7.4.3.108
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2023.Q4.0 <2023.Q4.3
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2023.Q3.1 <2023.Q3.6
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.GA <7.3u36
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.GA <7.4u93

## Details
Cross-site request forgery (CSRF) vulnerability in the content page editor in Liferay Portal 7.3.2 through 7.4.3.107, and Liferay DXP 2023.Q4.0 through 2023.Q4.2, 2023.Q3.1 through 2023.Q3.5, 7.4 GA through update 92 and 7.3 GA through update 35 allows remote attackers to (1) change user passwords, (2) shut down the server, (3) execute arbitrary code in the scripting console, (4) and perform other administrative actions via the p_l_back_url parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-26272
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2024-26272
