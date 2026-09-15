# [H] Liferay Portal and Liferay DXP insecure default configuration

## Summary
Severity: High
Advisory: GHSA-jfch-m2x3-2v66
CVE: CVE-2021-33321
CWE: CWE-640
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jfch-m2x3-2v66
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <5.11.0
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.3.3

## Details
Insecure default configuration in portal services implementation before 5.11.0 in Liferay Portal 6.2.3 through 7.3.2, and Liferay DXP before 7.3, allows remote attackers to enumerate user email address via the forgot password functionality. The portal.property login.secure.forgot.password should be defaulted to true.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33321
- https://github.com/liferay/liferay-portal/commit/06df28c5ad618afed967fa485418e6cc29c70f38
- https://github.com/liferay/liferay-portal/commit/37de1d78d9b1c4a473e3233a6ea146c741075e18
- https://github.com/liferay/liferay-portal
- https://help.liferay.com/hc/en-us/articles/360050785632
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120748055
