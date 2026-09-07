# [M] Liferay Vulnerable to Open Redirect via Adaptive Media Administration Page

## Summary
Severity: Medium
Advisory: GHSA-3mrr-cw9q-727m
CVE: CVE-2023-44308
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-3mrr-cw9q-727m
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.adaptive.media.web` — affected >=2023.Q3 <2023.Q3.6
- Maven: `com.liferay:com.liferay.adaptive.media.web` — affected >=7.4.0

## Details
Open redirect vulnerability in adaptive media administration page in Liferay DXP 2023.Q3 before patch 6, and 7.4 GA through update 92 allows remote attackers to redirect users to arbitrary external URLs via the _com_liferay_adaptive_media_web_portlet_AMPortlet_redirect parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44308
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-44308
