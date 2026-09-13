# [M] Liferay Publications is vulnerable to Incorrect Authorization

## Summary
Severity: Medium
Advisory: GHSA-894w-w643-qvxv
CVE: CVE-2025-62243
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-894w-w643-qvxv
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.change.tracking.web` — affected >=0 <2.0.122

## Details
Insecure direct object reference (IDOR) vulnerability in Publications in Liferay Portal 7.4.1 through 7.4.3.112, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, and 7.4 GA through update 92 allows remote authenticated attackers to view publication comments via the `_com_liferay_change_tracking_web_portlet_PublicationsPortlet_value` parameter.

Publications comments in Liferay Portal 7.4.1 through 7.4.3.112, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, and 7.4 GA through update 92 does not properly check user permissions, which allows remote authenticated users to edit publication comments via crafted URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62243
- https://github.com/liferay/liferay-portal/commit/8190bb30e8a111879d92e256bded575857696c5a
- https://github.com/liferay/liferay-portal/commit/e1457adf84fd596c6ec5a982adef97d7962347a4
- https://github.com/liferay/liferay-portal/commit/f68ecf7fd8e08aba5fb806eb61d2c0f8ec6adec8
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62243
