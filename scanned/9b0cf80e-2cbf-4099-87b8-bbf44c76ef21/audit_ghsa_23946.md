# [H] Liferay Portal and Liferay DXP Has Company Administrator Accounts Vulnerable to Takeovers

## Summary
Severity: High
Advisory: GHSA-5gh9-g62h-f35m
CVE: CVE-2021-33335
CWE: CWE-269, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5gh9-g62h-f35m
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.0.3 <7.3.5
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp20
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp9

## Details
Privilege escalation vulnerability in Liferay Portal 7.0.3 through 7.3.4, and Liferay DXP 7.1 before fix pack 20, and 7.2 before fix pack 9 allows remote authenticated users with permission to update/edit users to take over a company administrator user account by editing the company administrator user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33335
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17103
- https://web.archive.org/web/20220828222916/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120747906
