# [M] Liferay Portal Vulnerable to XSS via a Crafted Redirect Field

## Summary
Severity: Medium
Advisory: GHSA-jmjf-cmq5-7w25
CVE: CVE-2016-10404
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jmjf-cmq5-7w25
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.0.3-ga4

## Details
XSS exists in Liferay Portal before 7.0 CE GA4 via a crafted redirect field to modules/apps/foundation/frontend-js/frontend-js-spa-web/src/main/resources/META-INF/resources/init.jsp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10404
- https://github.com/liferay/liferay-portal/commit/333f65bae9106182d12e02d249d4f95e16e93fa2
- https://github.com/liferay/liferay-portal
- https://web.archive.org/web/20200601000000*/https://dev.liferay.com/web/community-security-team/known-vulnerabilities/liferay-portal-70/-/asset_publisher/cjE0ourZXJZE/content/cst-7017-multiple-xss-vulnerabilities
