# [M] Liferay Portal vulnerable to reflected cross-site scripting via the `redirect` parameter

## Summary
Severity: Medium
Advisory: GHSA-m4hg-46pw-6mmv
CVE: CVE-2025-43817
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-m4hg-46pw-6mmv
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.3.74-ga74 <7.4.3.112-ga112

## Details
Multiple reflected cross-site scripting (XSS) vulnerabilities in Liferay Portal 7.4.3.74 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.6, 2023.Q3.1 through 2023.Q3.8, and 7.4 update 74 through update 92 allow remote attackers to inject arbitrary web script or HTML via the `redirect` parameter to (1) Announcements, or (2) Alerts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43817
- https://github.com/liferay/liferay-portal/commit/40b9dcafccff4b0ba2a20ef4c9723bea820f814b
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17902
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43817
