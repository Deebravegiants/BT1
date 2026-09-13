# [M] Liferay Portal allows unrestricted upload of file in the style books component

## Summary
Severity: Medium
Advisory: GHSA-mf9q-87xx-jgvv
CVE: CVE-2025-43766
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-23
Source: https://github.com/advisories/GHSA-mf9q-87xx-jgvv
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.style.book.web` — affected >=0 <2.0.117

## Details
The Liferay Portal 7.4.0 through 7.3.3.131, and Liferay DXP 2024.Q4.0, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.12 and 7.4 GA through update 92 allows the upload of unrestricted files in the style books component that are processed within the environment enabling arbitrary code execution by attackers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43766
- https://github.com/liferay/liferay-portal/commit/d4a5b8fc9f88468168603ff8a1f9b81fa5b7c43e
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18145
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43766
