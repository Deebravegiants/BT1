# [M] Liferay Portal Vulnerable to XSS in Web Content translation

## Summary
Severity: Medium
Advisory: GHSA-qh92-cr5f-3595
CVE: CVE-2025-43826
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-01
Source: https://github.com/advisories/GHSA-qh92-cr5f-3595
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.113-ga113

## Details
Stored Cross-site Scripting (XSS) vulnerabilities in Web Content translation in Liferay Portal 7.4.0 through 7.4.3.112, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.8, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and older unsupported versions allow remote attackers to inject arbitrary web script or HTML via any rich text field in a web content article.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43826
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17939
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43826
