# [M] Liferay Portal's selection modal is vulnerable to XSS

## Summary
Severity: Medium
Advisory: GHSA-g8fh-pfw3-8rmr
CVE: CVE-2025-43787
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-12
Source: https://github.com/advisories/GHSA-g8fh-pfw3-8rmr
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.users.admin.web` — affected >=6.0.6 <11.0.33

## Details
A stored cross-site scripting vulnerability in the Liferay Portal  7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q3.0, 2025.Q2.0 through 2025.Q2.12, 2025.Q1.0 through 2025.Q1.17, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13 and 2024.Q1.1 through 2024.Q1.20 allows an remote authenticated attacker to inject JavaScript through the organization site names. The malicious payload is stored and executed without proper sanitization or escaping.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43787
- https://github.com/liferay/liferay-portal/commit/b230afddd5125dc5f858d68011ef93e9c47703a6
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43787
