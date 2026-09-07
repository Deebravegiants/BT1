# [M] Liferay Portal and Liferay DXP Allows Arbitrary Redirect of Users to External URLs

## Summary
Severity: Medium
Advisory: GHSA-mj8w-h522-jwm8
CVE: CVE-2021-33331
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mj8w-h522-jwm8
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.0.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.10.fp0 <7.0.10.fp94
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp8

## Details
Open redirect vulnerability in the Notifications module in Liferay Portal 7.0.0 through 7.3.1, and Liferay DXP 7.0 before fix pack 94, 7.1 before fix pack 19 and 7.2 before fix pack 8, allows remote attackers to redirect users to arbitrary external URLs via the 'redirect' parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33331
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17022
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120747627
