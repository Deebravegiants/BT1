# [M] Liferay Portal Vulnerable to Cross-Site Scripting (XSS) via Categories Admin Page

## Summary
Severity: Medium
Advisory: GHSA-239w-4f3w-cfcv
CVE: CVE-2021-29039
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-239w-4f3w-cfcv
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.4 <7.3.5

## Details
Cross-site scripting (XSS) vulnerability in the Asset module's categories administration page in Liferay Portal 7.3.4 allows remote attackers to inject arbitrary web script or HTML via the site name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29039
- https://github.com/liferay/liferay-portal
- https://web.archive.org/web/20220828222833/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120777766
- http://liferay.com
