# [M] Liferay Portal Reflected XSS in blogs-web

## Summary
Severity: Medium
Advisory: GHSA-6qcg-28jh-hm7r
CVE: CVE-2025-4576
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-6qcg-28jh-hm7r
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.blogs.web` — affected >=0 <6.0.139

## Details
A reflected cross-site scripting (XSS) vulnerability in the Liferay Portal 7.4.0 through 7.4.3.133, and Liferay DXP 2025.Q1.0 through 2025.Q1.4 ,2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.15, 7.4 GA through update 92 allows an remote non-authenticated attacker to inject JavaScript into the `modules/apps/blogs/blogs-web/src/main/resources/META-INF/resources/blogs/entry_cover_image_caption.jsp`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4576
- https://github.com/liferay/liferay-portal/commit/afd9e7751fff6f573699ef1169da279957f72428
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18194
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-4576
