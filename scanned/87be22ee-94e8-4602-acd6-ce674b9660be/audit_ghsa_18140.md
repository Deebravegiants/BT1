# [M] Liferay Portal vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-5c6v-fqcw-w6q5
CVE: CVE-2025-43791
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-5c6v-fqcw-w6q5
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.dynamic.data.mapping.form.field.type` — affected >=0 <6.0.167

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Liferay Portal 7.3.0 through 7.4.3.111, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92 and 7.3 GA through update 36 allow remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a "Rich Text" type field to (1) a web content structure, (2) a Documents and Media Document Type , or (3) custom assets that uses the Data Engine's module Rich Text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43791
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43791
