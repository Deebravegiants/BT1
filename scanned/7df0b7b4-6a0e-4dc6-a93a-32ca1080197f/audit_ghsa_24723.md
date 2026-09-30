# [M] Liferay Portal and Liferay DXP Fails to Check Permissions

## Summary
Severity: Medium
Advisory: GHSA-pr7v-qv65-rp9m
CVE: CVE-2021-29052
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pr7v-qv65-rp9m
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.3.10.fp1

## Details
The Data Engine module in Liferay Portal 7.3.0 through 7.3.5, and Liferay DXP 7.3 before fix pack 1 does not check permissions in DataDefinitionResourceImpl.getSiteDataDefinitionByContentTypeByDataDefinitionKey, which allows remote authenticated users to view DDMStructures via GET API calls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29052
- https://github.com/liferay/liferay-portal
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120743159
- http://liferay.com
