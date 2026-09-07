# [M] Liferay Portal is vulnerable to Stored XSS through Forms text type field

## Summary
Severity: Medium
Advisory: GHSA-378f-8q54-3fqx
CVE: CVE-2025-43830
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-378f-8q54-3fqx
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.2 <7.4.3.112-ga112

## Details
Stored cross-site scripting (XSS) vulnerability in Forms in Liferay Portal 7.3.2 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, 7.4 GA through update 92, and 7.3 GA through update 35 allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a form with a rich text type field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43830
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43830
