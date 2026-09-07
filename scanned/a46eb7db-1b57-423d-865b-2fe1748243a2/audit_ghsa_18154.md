# [M] Liferay Portal is vulnerable to XSS attacks via its remote app title field

## Summary
Severity: Medium
Advisory: GHSA-88g3-pv3w-5wmr
CVE: CVE-2025-43775
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-88g3-pv3w-5wmr
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.client.extension.web` — affected >=1.0.71 <2.0.27

## Details
A stored cross-site scripting (XSS) vulnerability in Liferay Portal 7.4.0 through 7.4.3.128, and Liferay DXP 2024.Q3.0 through 2024.Q3.5, 2024.Q2.0 through 2024.Q2.12, 2024.Q1.1 through 2024.Q1.12, and 7.4 GA through update 92 allows remote attackers to inject arbitrary web script or HTML via remote app title field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43775
- https://github.com/liferay/liferay-portal/commit/e54b2b41564df4f11cfa77b3e6c4353cf0a3b16d
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18123
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43775
