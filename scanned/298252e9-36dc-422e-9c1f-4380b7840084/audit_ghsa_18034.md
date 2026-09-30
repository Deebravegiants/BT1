# [M] Liferay Portal Email Modification Vulnerability via Calendar Portlet

## Summary
Severity: Medium
Advisory: GHSA-7mxq-h2r7-h449
CVE: CVE-2025-43739
CWE: CWE-203
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-7mxq-h2r7-h449
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.calendar.service` — affected >=0 <6.0.83

## Details
Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.6, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.16 and 7.4 GA through update 92 allow any authenticated user to modify the content of emails sent through the calendar portlet, allowing an attacker to send phishing emails to any other user in the same organization.

Liferay Portal is fixed on the master branch from commit ff18e7d.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43739
- https://github.com/liferay/liferay-portal/commit/0a9f5df16ae0afa8216ca568b89b2cdf00054bde
- https://github.com/liferay/liferay-portal/commit/5dc74a9f53f0aaa6cc1b6e0f503842832324239a
- https://github.com/liferay/liferay-portal/commit/75be892f7cf31e1a38555d45627b0c2a06490d3d
- https://github.com/liferay/liferay-portal/commit/7d70fab2259ff8b4a775021eb95bfc183823f8fc
- https://github.com/liferay/liferay-portal/commit/7eb551616c6b8beeaf660ff7f29b09794cb80d91
- https://github.com/liferay/liferay-portal/commit/a01a99cc4a5c7436f49790a1bfb386299172149c
- https://github.com/liferay/liferay-portal/commit/b396c00338e754976a9f63ea1d5393f29babdabb
- https://github.com/liferay/liferay-portal/commit/c1660f1a906c5ee3adca51e68f0abd6f9c1d253f
- https://github.com/liferay/liferay-portal/commit/e50c1a0a53d30b4e55f47495e265c5b7ea3459e1
- https://github.com/liferay/liferay-portal/commit/f238677d9afb46cfe4e23f05ce11bd5197a70388
- https://github.com/liferay/liferay-portal/commit/ff18e7d363f2a3bc83e9d3446f1bc49bee821883
- https://github.com/liferay/liferay-portal/commit/ff927f3f6784b396d3a611ac2e5e99b69ff0fd05
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18210
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43739
