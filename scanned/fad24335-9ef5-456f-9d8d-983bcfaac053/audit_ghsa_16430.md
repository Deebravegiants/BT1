# [H] Liferay Portal and Liferay DXP Vulnerable to Cross-Site Request Forgery in Terms of Use Page

## Summary
Severity: High
Advisory: GHSA-mh9r-9pcx-rx55
CVE: CVE-2021-29050
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-mh9r-9pcx-rx55
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <5.25.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp11

## Details
Cross-Site Request Forgery (CSRF) vulnerability in the terms of use page in the implementation for the portal services package before 5.25.0 from Liferay Portal (before 7.3.6), and Liferay DXP 7.3 before service pack 1, 7.2 before fix pack 11 allows remote attackers to accept the site's terms of use via social engineering and enticing the user to visit a malicious page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29050
- https://github.com/liferay/liferay-portal/commit/1295dcd8173ac820e501d0e9b3bf1da97ea8b7d4
- https://github.com/liferay/liferay-portal/commit/f2723cb2e8dacfbd140ff5f255bb7d21a11c476d
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17207
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2021-29050
