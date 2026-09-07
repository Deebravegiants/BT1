# [M] Liferay Portal Vulnerable to Reflected XSS via the selectedLanguageId Parameter

## Summary
Severity: Medium
Advisory: GHSA-2j97-4jmq-c4xf
CVE: CVE-2025-62264
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-31
Source: https://github.com/advisories/GHSA-2j97-4jmq-c4xf
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.3.8 <7.4.3.112-ga112

## Details
Reflected cross-site scripting (XSS) vulnerability in Languauge Override in Liferay Portal 7.4.3.8 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, and 7.4 update 4 through update 92 allows remote attackers to inject arbitrary web script or HTML via the `_com_liferay_portal_language_override_web_internal_portlet_PLOPortlet_selectedLanguageId` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62264
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62264
