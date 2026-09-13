# [M] Liferay Portal and Liferay DXP Don't Check Permissions of Pages

## Summary
Severity: Medium
Advisory: GHSA-474f-cmx5-gm69
CVE: CVE-2021-33324
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-474f-cmx5-gm69
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.1.0 <7.3.2
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.1.10.fp20
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp5

## Details
The Layout module in Liferay Portal 7.1.0 through 7.3.1, and Liferay DXP 7.1 before fix pack 20, and 7.2 before fix pack 5, does not properly check permission of pages, which allows remote authenticated users without view permission of a page to view the page via a site's page administration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33324
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17001
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120747063
- https://web.archive.org/web/20220828222955/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120747063
