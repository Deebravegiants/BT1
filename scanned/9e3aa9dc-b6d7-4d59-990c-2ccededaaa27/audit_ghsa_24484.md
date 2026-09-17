# [H] Liferay Portal and Liferay DXP Vulnerable to Multiple SQL Injections

## Summary
Severity: High
Advisory: GHSA-f9wj-c5pc-g9rh
CVE: CVE-2021-29053
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f9wj-c5pc-g9rh
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.5 <7.3.6
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.3.10.fp1

## Details
Multiple SQL injection vulnerabilities in Liferay Portal 7.3.5 and Liferay DXP 7.3 before fix pack 1 allow remote authenticated users to execute arbitrary SQL commands via the classPKField parameter to (1) CommerceChannelRelFinder.countByC_C, or (2) CommerceChannelRelFinder.findByC_C.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29053
- https://github.com/liferay/liferay-portal
- https://web.archive.org/web/20221121171927/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120778225
- http://liferay.com
