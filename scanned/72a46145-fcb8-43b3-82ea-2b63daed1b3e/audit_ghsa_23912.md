# [M] Liferay Portal Vulnerable to XSS via Mishandled Title or Summary in the Web Content Display

## Summary
Severity: Medium
Advisory: GHSA-6q67-5wvc-rmw9
CVE: CVE-2017-12649
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6q67-5wvc-rmw9
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.0.3-ga4

## Details
XSS exists in Liferay Portal before 7.0 CE GA4 via a crafted title or summary that is mishandled in the Web Content Display.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12649
- https://github.com/brianchandotcom/liferay-portal/pull/47579
- https://github.com/liferay/liferay-portal
- https://web.archive.org/web/20200901000000*/https://dev.liferay.com/web/community-security-team/known-vulnerabilities/liferay-portal-70/-/asset_publisher/cjE0ourZXJZE/content/cst-7017-multiple-xss-vulnerabilities
