# [M] Liferay Portal Cross-Site Request Forgery (CSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-697h-3q6m-jwp4
CVE: CVE-2025-43809
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-19
Source: https://github.com/advisories/GHSA-697h-3q6m-jwp4
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <101.0.0

## Details
Cross-Site Request Forgery (CSRF) vulnerability in the server (license) registration page in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.7, 2023.Q3.1 through 2023.Q3.9, 7.4 GA through update 92, and older unsupported versions allows remote attackers to register a server license via the 'orderUuid' parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43809
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43809
