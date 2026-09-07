# [M] Liferay Portal has stored cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r45v-2289-jgr4
CVE: CVE-2025-43794
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-r45v-2289-jgr4
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <99.0.0

## Details
A stored cross-site scripting (XSS) vulnerability in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows remote authenticated attackers with the instance administrator role to inject arbitrary web script or HTML into all pages via a crafted payload injected into the Instance Configuration's (1) CDN Host HTTP text field or (2) CDN Host HTTPS text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43794
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43794
