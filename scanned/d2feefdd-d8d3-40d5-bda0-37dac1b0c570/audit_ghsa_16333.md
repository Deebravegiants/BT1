# [M] Liferay Portal and Liferay DXP Does Not Obfuscate Password Reminder Answers

## Summary
Severity: Medium
Advisory: GHSA-mwhf-6mjm-6w3h
CVE: CVE-2021-29038
CWE: CWE-640
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-mwhf-6mjm-6w3h
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:portal-impl` — affected >=0 <5.18.4
- Maven: `com.liferay:com.liferay.users.admin.web` — affected >=0 <5.0.33
- Maven: `com.liferay:com.liferay.login.web` — affected >=0 <5.0.18
- Maven: `com.liferay.commerce:com.liferay.commerce.account.web` — affected >=0 <3.0.7
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp17
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.fp1

## Details
In Liferay Impl before 5.18.4, Liferay Users Admin Web before 5.0.33, Liferay Login Web before 5.0.18, and Liferay Commerce Account Web before 3.0.7 from Liferay Portal (7.2.0 through 7.3.5), and older unsupported versions, and Liferay DXP 7.3 before fix pack 1, 7.2 before fix pack 17, and older unsupported versions does not obfuscate password reminder answers on the page, which allows attackers to use man-in-the-middle or shoulder surfing attacks to steal user's password reminder answers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29038
- https://github.com/liferay/liferay-portal/commit/5e2da784aeefce64107abd0411590db2b55faf0b
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2021-29038
