# [M] Liferay Portal vulnerable to path traversal and denial-of-service in the ComboServlet

## Summary
Severity: Medium
Advisory: GHSA-2hm7-r8f3-423h
CVE: CVE-2025-43813
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-2hm7-r8f3-423h
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.108-ga108
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <96.0.0

## Details
Possible path traversal vulnerability and denial-of-service in the ComboServlet in Liferay Portal 7.4.0 through 7.4.3.107, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.4, 2023.Q3.1 through 2023.Q3.8, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows remote attackers to access arbitrary CSS and JSS files and load the files multiple times via the query string in a URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43813
- https://github.com/liferay/liferay-portal/commit/7acad68976e831a0f3b855752ad7874e03be1d43
- https://github.com/liferay/liferay-portal/commit/9159075ede8a1656bf67a893a486c93a9e9fe70a
- https://github.com/liferay/liferay-portal/commit/9be57d358ae0f6181a138ce08f52b80e4b14778a
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17865
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43813
