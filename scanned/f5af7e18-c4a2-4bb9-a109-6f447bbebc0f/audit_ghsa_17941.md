# [M] Liferay Portal vulnerable to Stored XSS in Components portlet

## Summary
Severity: Medium
Advisory: GHSA-rvmf-jw8g-r35r
CVE: CVE-2025-43769
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-23
Source: https://github.com/advisories/GHSA-rvmf-jw8g-r35r
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.plugins.admin.web` — affected >=0 <5.0.36

## Details
Stored cross-site scripting (XSS) vulnerability in Liferay Portal 7.4.0 through 7.4.3.131, and Liferay DXP 2024.Q3.1 through 2024.Q3.8, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.12 and 7.4 GA through update 92 allows remote attackers to execute arbitrary web script or HTML via components tab.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43769
- https://github.com/liferay/liferay-portal/commit/0249230a00a8ab42a5edaf6bca1bcf594525c0e9
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18128
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43769
