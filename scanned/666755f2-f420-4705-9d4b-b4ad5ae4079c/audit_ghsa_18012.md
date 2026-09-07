# [M] Liferay Portal stored cross-site scripting in text field of the web content structure

## Summary
Severity: Medium
Advisory: GHSA-h8gx-4hhm-w45v
CVE: CVE-2025-43765
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-23
Source: https://github.com/advisories/GHSA-h8gx-4hhm-w45v
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.journal.service` — affected >=0 <7.0.161

## Details
A Stored cross-site scripting vulnerability in the Liferay Portal 7.4.0 through 7.4.3.131, and Liferay DXP 2024.Q4.0, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.13 and 7.4 GA through update 92 allows an remote non-authenticated attacker to inject JavaScript into the text field from a web content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43765
- https://github.com/liferay/liferay-portal/commit/6aa0adb0e8d47794e942fd87074cf05755a2d9bc
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18150
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43765
