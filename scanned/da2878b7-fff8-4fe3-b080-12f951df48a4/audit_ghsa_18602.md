# [M] Liferay Portal is vulnerable to XSS through its Commerce Search Result widget

## Summary
Severity: Medium
Advisory: GHSA-xx7h-2wf7-hc7p
CVE: CVE-2025-43823
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-xx7h-2wf7-hc7p
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0 <7.4.3.112-ga112

## Details
Cross-site Scripting (XSS) vulnerability in the Commerce Search Result widget in Liferay Portal 7.4.0 through 7.4.3.111, and Liferay DXP 2023.Q4 before patch 6, 2023.Q3 before patch 9, and 7.4 GA through update 92 allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a Commerce Product's Name text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43823
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43823
