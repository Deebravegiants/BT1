# [M] Liferay Portal Allows Cross-Site Scripting (XSS) via the SimpleCaptcha API

## Summary
Severity: Medium
Advisory: GHSA-hwp2-gvm5-452f
CVE: CVE-2019-6588
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hwp2-gvm5-452f
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.1.0

## Details
In Liferay Portal before 7.1 CE GA4, an XSS vulnerability exists in the SimpleCaptcha API when custom code passes unsanitized input into the "url" parameter of the JSP taglib call <liferay-ui:captcha url="<%= url %>" /> or <liferay-captcha:captcha url="<%= url %>" />. Liferay Portal out-of-the-box behavior with no customizations is not vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6588
- https://dev.liferay.com/web/community-security-team/known-vulnerabilities/liferay-portal-71/-/asset_publisher/7v4O7y85hZMo/content/cst-7130-multiple-xss-vulnerabilities-in-7-1-ce-ga3
- https://github.com/liferay/liferay-portal
- http://packetstormsecurity.com/files/153252/Liferay-Portal-7.1-CE-GA4-Cross-Site-Scripting.html
