# [M] Liferay Portal Commerce Shop is vulnerable to Stored XSS through SVG file

## Summary
Severity: Medium
Advisory: GHSA-893r-jr58-3hxr
CVE: CVE-2025-43829
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-893r-jr58-3hxr
Type: github-advisory

## Affected
- Maven: `com.liferay.commerce:com.liferay.commerce.shop.by.diagram.web` — affected >=1.0.41 <1.0.83

## Details
There is a Stored Cross-Site Scripting (XSS) vulnerability in diagram type products in Commerce in Liferay Portal 7.4.3.18 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, and 7.4 update 18 through update 92. This vulnerability allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a SVG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43829
- https://github.com/liferay/liferay-portal/commit/288ba1f41f8c3374c80d7af27346eeebb8c780d0
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43829
