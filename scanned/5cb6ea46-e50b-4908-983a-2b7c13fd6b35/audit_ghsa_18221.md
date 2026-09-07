# [M] Liferay Portal Cross-site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jfv5-r382-xvwh
CVE: CVE-2025-43800
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-jfv5-r382-xvwh
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.dynamic.data.mapping.form.field.type` — affected >=0 <6.0.167

## Details
Cross-site scripting (XSS) vulnerability in Objects in Liferay Portal 7.4.3.20 through 7.4.3.111, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4 and 7.4 GA through update 92 allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into an object with a rich text type field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43800
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43800
