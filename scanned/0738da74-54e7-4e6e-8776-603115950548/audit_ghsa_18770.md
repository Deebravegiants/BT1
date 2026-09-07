# [H] Liferay Portal Vulnerable to CSRF in Headless APIs

## Summary
Severity: High
Advisory: GHSA-gh4w-8qgq-8w9r
CVE: CVE-2025-62258
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-gh4w-8qgq-8w9r
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.108

## Details
CSRF vulnerability in Headless API in Liferay Portal 7.4.0 through 7.4.3.107, and Liferay DXP 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows remote attackers to execute any Headless API via the `endpoint` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62258
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62258
