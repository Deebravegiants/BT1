# [M] Liferay Portal and Liferay DXP Reveals Data via Overly Verbose Error Messages

## Summary
Severity: Medium
Advisory: GHSA-87x7-pwrx-jch7
CVE: CVE-2021-29040
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-87x7-pwrx-jch7
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.3.5
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.0.10.fp97
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp20
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp10

## Details
The JSON web services in Liferay Portal 7.3.4 and earlier, and Liferay DXP 7.0 before fix pack 97, 7.1 before fix pack 20 and 7.2 before fix pack 10 may provide overly verbose error messages, which allows remote attackers to use the contents of error messages to help launch another, more focused attacks via crafted inputs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29040
- https://github.com/liferay/liferay-portal
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120743429
- https://web.archive.org/web/20220828222656/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120743429
- http://liferay.com
