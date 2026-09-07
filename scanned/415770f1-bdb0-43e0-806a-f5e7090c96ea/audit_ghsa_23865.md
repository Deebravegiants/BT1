# [M] Liferay Portal Vulnerable to Persistent Cross-Site Scripting (XSS) in MyAccountPortlet

## Summary
Severity: Medium
Advisory: GHSA-f99h-h678-fgg4
CVE: CVE-2020-7934
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f99h-h678-fgg4
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.1.0 <7.3.0

## Details
In LifeRay Portal CE 7.1.0 through 7.2.1, the First Name, Middle Name, and Last Name fields for user accounts in MyAccountPortlet are all vulnerable to a persistent XSS issue. Any user can modify these fields with a particular XSS payload, and it will be stored in the database. The payload will then be rendered when a user utilizes the search feature to search for other users (i.e., if a user with modified fields occurs in the search results).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7934
- https://github.com/3ndG4me/liferay-xss-7.2.1GA2-poc-report-CVE-2020-7934
- https://github.com/liferay/liferay-portal
- https://web.archive.org/web/20200808034429/https://semanticbits.com/liferay-portal-authenticated-xss-disclosure
- http://packetstormsecurity.com/files/160168/LifeRay-7.2.1-GA2-Cross-Site-Scripting.html
