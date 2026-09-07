# [M] Liferay Portal's Membership page is vulnerable to XSS through “name“ text field

## Summary
Severity: Medium
Advisory: GHSA-xw6m-3m5q-mxpm
CVE: CVE-2025-62238
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-xw6m-3m5q-mxpm
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.account.admin.web` — affected >=2.0.40 <2.0.114

## Details
Stored cross-site scripting (XSS) vulnerability on the Membership page in Account Settings in Liferay Portal 7.4.3.21 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, and 7.4 update 21 through update 92 allows remote authenticated attackers to inject arbitrary web script or HTML via a crafted payload injected into a Account's “Name“ text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62238
- https://github.com/liferay/liferay-portal/commit/89a043bface29bf924e25d1c2c3b05f85d750a75
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17920
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62238
