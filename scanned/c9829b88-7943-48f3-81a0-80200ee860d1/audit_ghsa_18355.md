# [M] Liferay Portal has unchecked input for loop condition vulnerability in XML-RPC

## Summary
Severity: Medium
Advisory: GHSA-95h4-8mqc-4mpf
CVE: CVE-2025-43801
CWE: CWE-606
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-95h4-8mqc-4mpf
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <101.0.0

## Details
Unchecked input for loop condition vulnerability in XML-RPC in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows remote attackers to perform a denial-of-service (DoS) attacks via a crafted XML-RPC request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43801
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43801
