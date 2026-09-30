# [M] Liferay Portal and Liferay DXP Stores User Passwords in Cleartext

## Summary
Severity: Medium
Advisory: GHSA-6c88-gvxw-f5hg
CVE: CVE-2021-33325
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6c88-gvxw-f5hg
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.0.10.fp93
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp7

## Details
The Portal Workflow module in Liferay Portal 7.3.2 and earlier, and Liferay DXP 7.0 before fix pack 93, 7.1 before fix pack 19, and 7.2 before fix pack 7, user's clear text passwords are stored in the database if workflow is enabled for user creation, which allows attackers with access to the database to obtain a user's password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33325
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17042
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120748389
