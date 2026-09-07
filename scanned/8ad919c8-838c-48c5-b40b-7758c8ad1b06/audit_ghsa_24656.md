# [M] Liferay Portal XSS vulnerability via movie parameter in the /html/portal/flash.jsp page

## Summary
Severity: Medium
Advisory: GHSA-2ggw-8gmc-r2gq
CVE: CVE-2017-1000425
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2ggw-8gmc-r2gq
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.1.0-a1

## Details
Cross-site scripting (XSS) vulnerability in the /html/portal/flash.jsp page in Liferay Portal CE 7.0 GA4 and older allows remote attackers to inject arbitrary web script or HTML via a javascript: URI in the "movie" parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000425
- https://github.com/liferay/liferay-portal/commit/9435af4ef8a90b5333da925a5ec860a43d18c031
- https://dev.liferay.com/web/community-security-team/known-vulnerabilities/-/asset_publisher/4AHAYapUm8Xc/content/cst-7030-multiple-xss-vulnerabilities-in-7-0-ce-ga4
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-15937
