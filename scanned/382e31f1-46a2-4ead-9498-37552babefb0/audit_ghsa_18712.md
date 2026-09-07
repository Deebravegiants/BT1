# [M] Liferay Portal is vulnerable to XSS in the Blogs widget

## Summary
Severity: Medium
Advisory: GHSA-56jv-4ww3-65mw
CVE: CVE-2025-62265
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-30
Source: https://github.com/advisories/GHSA-56jv-4ww3-65mw
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.112-ga112

## Details
Cross-site scripting (XSS) vulnerability in the Blogs widget in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.8, 7.4 GA through update 92, 7.3 GA through update 36, and older unsupported versions allows remote attackers to inject arbitrary web script or HTML via a crafted <iframe> injected into a blog entry's “Content” text field.

The Blogs widget in Liferay DXP does not add the sandbox attribute to <iframe> elements, which allows remote attackers to access the parent page via scripts and links in the frame page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62265
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62265
