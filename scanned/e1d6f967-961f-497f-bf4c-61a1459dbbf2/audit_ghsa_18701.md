# [M] Liferay Portal is vulnerable to XSS through its Commerce Product's Name text field

## Summary
Severity: Medium
Advisory: GHSA-fjrp-77f3-43xj
CVE: CVE-2025-43821
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-fjrp-77f3-43xj
Type: github-advisory

## Affected
- Maven: `com.liferay.commerce:com.liferay.commerce.product.service` — affected >=6.0.5 <6.0.134

## Details
Cross-site Scripting (XSS) vulnerability in the Commerce Product Comparison Table widget in Liferay Portal 7.4.0 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, and 7.4 GA through update 92 allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a Commerce Product's Name text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43821
- https://github.com/liferay/liferay-portal/commit/433f82c03fac10167f1f811efb482d6010bac6db
- https://github.com/liferay/com-liferay-commerce
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43821
