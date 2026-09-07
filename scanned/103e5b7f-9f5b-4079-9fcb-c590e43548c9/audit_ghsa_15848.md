# [C] Liferay Portal and Liferay DXP Vulnerable to CSRF in the Script Console

## Summary
Severity: Critical
Advisory: GHSA-chj2-4vg7-hhg3
CVE: CVE-2024-8980
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-22
Source: https://github.com/advisories/GHSA-chj2-4vg7-hhg3
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.0.0-a1 <7.4.3.102-GA102
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=2023.Q3.1 <2023.Q3.5
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.0-GA
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0-GA
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0.GA
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0-GA <7.3.10.u36
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0-GA

## Details
The Script Console in Liferay Portal 7.0.0 through 7.4.3.101, and Liferay DXP 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, 7.2 GA through fix pack 20, 7.1 GA through fix pack 28, 7.0 GA through fix pack 102 and 6.2 GA through fix pack 173 does not sufficiently protect against Cross-Site Request Forgery (CSRF) attacks, which allows remote attackers to execute arbitrary Groovy script via a crafted URL or a XSS vulnerability. This issue has been patched in Liferay Portal 7.4.3.102, Liferay DXP 2024.Q1.1, Liferay DXP 2023.Q4.0, Liferay DXP 2023.Q3.5, and Liferay DXP 7.3 Update 36.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8980
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2024-8980
