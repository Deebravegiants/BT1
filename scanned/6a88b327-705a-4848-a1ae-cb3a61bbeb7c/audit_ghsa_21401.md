# [M] Incorrect Default Permissions in Liferay Portal

## Summary
Severity: Medium
Advisory: GHSA-wgqm-qp44-cg6x
CVE: CVE-2022-42128
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-wgqm-qp44-cg6x
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.1 <7.4.3.5

## Details
The Hypermedia REST APIs module in Liferay Portal 7.4.1 through 7.4.3.4, and Liferay DXP 7.4 GA does not properly check permissions, which allows remote attackers to obtain a WikiNode object via the WikiNodeResource.getSiteWikiNodeByExternalReferenceCode API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42128
- https://issues.liferay.com/browse/LPE-17595
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42128
- http://liferay.com
