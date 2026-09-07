# [M] Liferay Portal Vulnerable to Cross-Site Scripting (XSS) via User Name Parameter 

## Summary
Severity: Medium
Advisory: GHSA-pvpg-9553-f979
CVE: CVE-2020-25476
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pvpg-9553-f979
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2

## Details
Liferay CMS Portal version 7.1.3 and 7.2.1 have a blind persistent cross-site scripting (XSS) vulnerability in the user name parameter to Calendar. An attacker can insert the malicious payload on the username, lastname or surname fields of its own profile, and the malicious payload will be injected and reflected in the calendar of the user who submitted the payload. An attacker could escalate its privileges in case an admin visits the calendar that injected the payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25476
- https://github.com/community-security-team/liferay-portal/compare/7.1.3-ga4...7.1.3-cumulative.patch
- https://github.com/community-security-team/liferay-portal/compare/7.2.1-ga2...7.2.1-cumulative.patch
- https://github.com/liferay/liferay-portal
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/119318646
