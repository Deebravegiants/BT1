# [H] Inefficient Regular Expression Complexity in Liferay Portal 

## Summary
Severity: High
Advisory: GHSA-vjj4-qwcm-552h
CVE: CVE-2022-42124
CWE: CWE-1333
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-vjj4-qwcm-552h
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.2 <7.4.3.5

## Details
ReDoS vulnerability in LayoutPageTemplateEntryUpgradeProcess in Liferay Portal 7.3.2 through 7.4.3.4 and Liferay DXP 7.2 fix pack 9 through fix pack 18, 7.3 before update 4, and DXP 7.4 GA allows remote attackers to consume an excessive amount of server resources via a crafted payload injected into the 'name' field of a layout prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42124
- https://issues.liferay.com/browse/LPE-17435
- https://issues.liferay.com/browse/LPE-17535
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42124
- http://liferay.com
