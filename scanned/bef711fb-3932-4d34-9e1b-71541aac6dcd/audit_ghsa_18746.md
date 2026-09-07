# [M] Liferay Mentions Web is Vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-mj68-2xr5-28xh
CVE: CVE-2025-62246
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-mj68-2xr5-28xh
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.mentions.web` — affected >=0 <6.0.35

## Details
Multiple stored cross-site scripting (XSS) vulnerabilities in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, 7.4 GA through update 92, and older unsupported versions allow remote authenticated users to inject arbitrary web script or HTML via a crafted payload injected into a user’s first, middle or last name text field to (1) page comments widget, (2) blog entry comments, (3) document and media document comments, (4) message board messages, (5) wiki page comments or (6) other widgets/apps that supports mentions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62246
- https://github.com/liferay/liferay-portal/commit/4218ecd902dbd860d3f9ee233b0ffa4c822a49ee
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17940
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62246
