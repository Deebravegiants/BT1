# [M] Liferay Portal vulnerable to cross-site scripting in the web content template

## Summary
Severity: Medium
Advisory: GHSA-jv8x-mm3v-75r7
CVE: CVE-2025-43812
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-jv8x-mm3v-75r7
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.3.4-ga4 <7.4.3.112-ga112
- Maven: `com.liferay:com.liferay.journal.web` — affected >=5.0.34 <5.0.161

## Details
Cross-site scripting (XSS) vulnerability in web content template in Liferay Portal 7.4.3.4 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.4, 2023.Q3.1 through 2023.Q3.8, and 7.4 GA through update 92 allows remote authenticated users to inject arbitrary web script or HTML via a crafted payload injected into a web content structure's Name text field

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43812
- https://github.com/liferay/liferay-portal/commit/7466c9ba0126a4a93c85913cbec9b11c687deb36
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17942
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43812
