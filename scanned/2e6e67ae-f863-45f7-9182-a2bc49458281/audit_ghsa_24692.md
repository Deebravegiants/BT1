# [M] Exposure of Resource to Wrong Sphere in Liferay Portal

## Summary
Severity: Medium
Advisory: GHSA-6xxc-4jc4-7jv3
CVE: CVE-2021-33330
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6xxc-4jc4-7jv3
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.3.3

## Details
Liferay Portal 7.2.0 through 7.3.2, and Liferay DXP 7.2 before fix pack 9, allows access to Cross-origin resource sharing (CORS) protected resources if the user is only authenticated using the portal session authentication, which allows remote attackers to obtain sensitive information including the targeted user’s email address and current CSRF token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33330
- https://issues.liferay.com/browse/LPE-17127
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120747720
