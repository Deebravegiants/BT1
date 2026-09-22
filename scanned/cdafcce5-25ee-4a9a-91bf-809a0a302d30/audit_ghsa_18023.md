# [M] Liferay Portal CAPTCHA Bypass for Gogo Shell

## Summary
Severity: Medium
Advisory: GHSA-3j6h-5v68-hvqg
CVE: CVE-2025-4604
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:A/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2025-08-05
Source: https://github.com/advisories/GHSA-3j6h-5v68-hvqg
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.captcha.impl` — affected >=0 <4.0.17

## Details
The vulnerable code can bypass the Captcha check in Liferay Portal 7.4.3.80 through 7.4.3.132, and Liferay DXP 2024.Q1.1 through 2024.Q1.19, 2024.Q2.0 through 2024.Q2.13, 2024.Q3.0 through 2024.Q3.13, 2024.Q4.0 through 2024.Q4.7, 2025.Q1.0 through 2025.Q1.15 and 7.4 update 80 through update 92 and then attackers can run scripts in the Gogo shell.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4604
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18168
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-4604
