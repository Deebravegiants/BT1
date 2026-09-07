# [M] Liferay Portal has multiple Stored XSS vulnerabilities on its View Order page

## Summary
Severity: Medium
Advisory: GHSA-4mqx-4p8g-995w
CVE: CVE-2025-43822
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-4mqx-4p8g-995w
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.3.15 <7.4.3.112-ga112

## Details
Multiple stored Cross-site Scripting (XSS) vulnerabilities in Liferay Portal 7.4.3.15 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, and 7.4 update 15 through update 92 allow remote attackers to inject arbitrary web script or HTML via crafted payload injected into a Terms and Condition's Name text field to (1) Payment Terms, or (2) the Delivery Term on the view order page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43822
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43822
